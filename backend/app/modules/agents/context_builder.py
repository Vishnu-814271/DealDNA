"""Context Builder.
Assembles current deal state, stakeholders, recent interactions, persistent memories,
and historical comparables into a structured, delimited prompt context.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models import Deal, Interaction, DealOutcome
from app.modules.memory.hindsight_adapter import hindsight_adapter


def build_deal_context(deal: Deal, db: Session, query: str) -> Dict[str, Any]:
    # 1. Company and Contact Details
    company_name = deal.company.name if deal.company else "Unknown Company"
    primary_contact = f"{deal.primary_contact.name} ({deal.primary_contact.role})" if deal.primary_contact else "None"

    # 2. Chronological interactions
    recent_interactions = (
        db.query(Interaction)
        .filter(Interaction.deal_id == deal.id)
        .order_by(Interaction.occurred_at.asc())
        .all()
    )
    interaction_summaries = [
        {
            "id": i.id,
            "type": i.type,
            "occurred_at": i.occurred_at.isoformat(),
            "content": i.content,
        }
        for i in recent_interactions
    ]

    # 3. Hindsight Memories (Recall)
    recalled_memories = hindsight_adapter.recall(query=query, deal_id=deal.id, limit=6)

    # 4. Historical Comparables (Deals with outcomes)
    historical_deals = (
        db.query(Deal)
        .join(DealOutcome, Deal.id == DealOutcome.deal_id)
        .filter(Deal.id != deal.id)
        .limit(5)
        .all()
    )
    comparables = [
        {
            "deal_id": hd.id,
            "deal_name": hd.name,
            "company": hd.company.name if hd.company else "",
            "stage": hd.stage,
            "outcomes": [
                {
                    "status": o.status,
                    "reason": o.reason,
                    "strategy": o.strategy_used,
                }
                for o in hd.outcomes
            ],
        }
        for hd in historical_deals
    ]

    return {
        "deal_id": deal.id,
        "deal_name": deal.name,
        "company_name": company_name,
        "primary_contact": primary_contact,
        "stage": deal.stage,
        "value": float(deal.value),
        "status": deal.status,
        "probability": deal.probability,
        "interactions": interaction_summaries,
        "memories": recalled_memories,
        "historical_comparables": comparables,
    }
