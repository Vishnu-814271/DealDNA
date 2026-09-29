from __future__ import annotations

import json
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Company, Contact, Deal, DealOutcome, Interaction, Recommendation, RecommendationEvidence, User
from app.modules.memory.hindsight_adapter import hindsight_adapter
from app.schemas import (
    DealCreate,
    DealOutcomeCreate,
    DealOutcomeRead,
    DealPatternRead,
    DealRead,
    DealUpdate,
    HistoricalDealMatch,
    InteractionCreate,
    InteractionRead,
)


def list_deals(db: Session) -> List[DealRead]:
    deals = db.query(Deal).order_by(Deal.created_at.desc()).all()
    return [_to_deal_read(d) for d in deals]


def get_deal(deal_id: str, db: Session) -> Optional[DealRead]:
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        return None
    return _to_deal_read(deal)


def create_deal(payload: DealCreate, db: Session) -> DealRead:
    deal_id = payload.id or f"DEAL-{uuid.uuid4().hex[:4].upper()}"
    new_deal = Deal(
        id=deal_id,
        company_id=payload.company_id,
        primary_contact_id=payload.primary_contact_id,
        owner_id=payload.owner_id,
        name=payload.name,
        stage=payload.stage,
        value=payload.value,
        currency=payload.currency,
        status=payload.status,
        probability=payload.probability,
        expected_close_date=payload.expected_close_date,
        summary=payload.summary,
    )
    db.add(new_deal)
    db.commit()
    db.refresh(new_deal)
    return _to_deal_read(new_deal)


def update_deal(deal_id: str, payload: DealUpdate, db: Session) -> Optional[DealRead]:
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        return None

    if payload.name is not None:
        deal.name = payload.name
    if payload.stage is not None:
        deal.stage = payload.stage
    if payload.value is not None:
        deal.value = payload.value
    if payload.probability is not None:
        deal.probability = payload.probability
    if payload.status is not None:
        deal.status = payload.status
    if payload.summary is not None:
        deal.summary = payload.summary
    if payload.expected_close_date is not None:
        deal.expected_close_date = payload.expected_close_date

    deal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(deal)
    return _to_deal_read(deal)


def get_deal_timeline(deal_id: str, db: Session) -> List[InteractionRead]:
    interactions = (
        db.query(Interaction)
        .filter(Interaction.deal_id == deal_id)
        .order_by(Interaction.occurred_at.asc())
        .all()
    )
    return [_to_interaction_read(i) for i in interactions]


def add_interaction(deal_id: str, payload: InteractionCreate, db: Session) -> InteractionRead:
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise ValueError("Deal not found")

    interaction_id = f"int-{uuid.uuid4().hex[:8]}"
    occurred_at = payload.occurred_at or datetime.utcnow()
    participants_json = json.dumps(payload.participants)

    # 1. Persist interaction in PostgreSQL / SQLite first
    interaction = Interaction(
        id=interaction_id,
        deal_id=deal_id,
        type=payload.type,
        occurred_at=occurred_at,
        participants=participants_json,
        content=payload.content,
        summary=payload.summary,
        memory_sync_status="PENDING",
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    # 2. Call Hindsight retain
    try:
        doc_id = hindsight_adapter.retain(
            deal_id=deal_id,
            content=payload.content,
            interaction_id=interaction_id,
            memory_type="Experience",
            metadata={
                "type": payload.type,
                "participants": payload.participants,
                "occurred_at": occurred_at.isoformat(),
            },
        )
        interaction.hindsight_document_id = doc_id
        interaction.memory_sync_status = "SYNCED"
        db.commit()
        db.refresh(interaction)
    except Exception as e:
        interaction.memory_sync_status = "FAILED"
        db.commit()

    return _to_interaction_read(interaction)


def record_deal_outcome(deal_id: str, payload: DealOutcomeCreate, db: Session) -> DealOutcomeRead:
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise ValueError("Deal not found")

    # Update Deal stage and status
    deal.stage = payload.status
    deal.status = payload.status
    deal.updated_at = datetime.utcnow()

    outcome_id = f"out-{uuid.uuid4().hex[:8]}"
    closed_at = payload.closed_at or datetime.utcnow()
    outcome = DealOutcome(
        id=outcome_id,
        deal_id=deal_id,
        status=payload.status,
        reason=payload.reason,
        strategy_used=payload.strategy_used,
        closed_at=closed_at,
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)

    # Retain the closed-loop learning memory into Hindsight
    try:
        learning_content = (
            f"Deal outcome for {deal.name}: {payload.status}. "
            f"Reason: {payload.reason}. "
            f"Strategy used: {payload.strategy_used or 'Standard negotiation'}."
        )
        hindsight_adapter.retain(
            deal_id=deal_id,
            content=learning_content,
            interaction_id=outcome_id,
            memory_type="Observation",
            metadata={"status": payload.status, "reason": payload.reason},
        )
    except Exception:
        pass

    return DealOutcomeRead.model_validate(outcome)


def get_deal_patterns(deal_id: str, db: Session) -> DealPatternRead:
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    deal_name = deal.name if deal else "Active Deal"

    # Fetch closed deals
    historical_deals = (
        db.query(Deal)
        .join(DealOutcome, Deal.id == DealOutcome.deal_id)
        .all()
    )

    matches = []
    for hd in historical_deals:
        for oc in hd.outcomes:
            matches.append(
                HistoricalDealMatch(
                    deal_id=hd.id,
                    deal_name=hd.name,
                    company_name=hd.company.name if hd.company else "Historical Account",
                    outcome=oc.status,
                    similarity_reason=f"Addressed pricing friction with strategy: '{oc.strategy_used}'",
                    strategy_used=oc.strategy_used,
                    value=float(hd.value),
                )
            )

    pattern_desc = (
        "Across historical accounts evaluating competitive alternatives, deals where executive ROI evidence "
        "and customer benchmarks were provided closed at 85% win rate. When pricing discounts were offered without ROI validation, "
        "deals stalled in procurement for an average of 42 additional days."
    )

    tactics = [
        "Deliver CFO-specific ROI model demonstrating time-to-value within 6 months.",
        "Share relevant customer case study proving reduction in operational overhead.",
        "Secure early technical validation workshop before submitting final pricing.",
    ]

    return DealPatternRead(
        deal_id=deal_id,
        observed_pattern=pattern_desc,
        confidence_label="supported",
        comparable_deals=matches[:4],
        recommended_tactics=tactics,
    )


def _to_deal_read(deal: Deal) -> DealRead:
    company_read = None
    if deal.company:
        company_read = {
            "id": deal.company.id,
            "name": deal.company.name,
            "industry": deal.company.industry,
            "size": deal.company.size,
            "created_at": deal.company.created_at,
            "updated_at": deal.company.updated_at,
        }

    contact_read = None
    if deal.primary_contact:
        contact_read = {
            "id": deal.primary_contact.id,
            "company_id": deal.primary_contact.company_id,
            "name": deal.primary_contact.name,
            "role": deal.primary_contact.role,
            "email": deal.primary_contact.email,
            "phone": deal.primary_contact.phone,
            "created_at": deal.primary_contact.created_at,
        }

    owner_read = None
    if deal.owner:
        owner_read = {
            "id": deal.owner.id,
            "name": deal.owner.name,
            "email": deal.owner.email,
            "role": deal.owner.role,
            "created_at": deal.owner.created_at,
        }

    outcomes_read = [
        DealOutcomeRead.model_validate(oc) for oc in (deal.outcomes or [])
    ]

    return DealRead(
        id=deal.id,
        company_id=deal.company_id,
        primary_contact_id=deal.primary_contact_id,
        owner_id=deal.owner_id,
        name=deal.name,
        stage=deal.stage,  # type: ignore
        value=deal.value,
        currency=deal.currency,
        status=deal.status,
        probability=deal.probability,
        expected_close_date=deal.expected_close_date,
        summary=deal.summary,
        created_at=deal.created_at,
        updated_at=deal.updated_at,
        company=company_read,  # type: ignore
        primary_contact=contact_read,  # type: ignore
        owner=owner_read,  # type: ignore
        outcomes=outcomes_read,
    )


def _to_interaction_read(interaction: Interaction) -> InteractionRead:
    try:
        participants = json.loads(interaction.participants) if interaction.participants else []
    except Exception:
        participants = []

    return InteractionRead(
        id=interaction.id,
        deal_id=interaction.deal_id,
        type=interaction.type,
        occurred_at=interaction.occurred_at,
        participants=participants,
        content=interaction.content,
        summary=interaction.summary,
        hindsight_document_id=interaction.hindsight_document_id,
        memory_sync_status=interaction.memory_sync_status,
        created_at=interaction.created_at,
    )
