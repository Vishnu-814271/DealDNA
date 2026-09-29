from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Recommendation, RecommendationEvidence
from app.schemas import RecommendationEvidenceRead, RecommendationRead


def get_recommendations_for_deal(deal_id: str, db: Session) -> List[RecommendationRead]:
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.deal_id == deal_id)
        .order_by(Recommendation.created_at.desc())
        .all()
    )
    
    results = []
    for r in recs:
        evidence_reads = [
            RecommendationEvidenceRead(
                id=e.id,
                interaction_id=e.interaction_id,
                evidence_type=e.evidence_type,
                reason=e.explanation,
            )
            for e in r.evidence
        ]
        results.append(
            RecommendationRead(
                id=r.id,
                deal_id=r.deal_id,
                query=r.query,
                recommendation=r.recommendation,
                confidence_label=r.confidence_label,  # type: ignore
                rationale=r.rationale,
                historical_pattern=r.historical_pattern,
                next_action=r.next_action,
                caveats=r.caveats,
                evidence=evidence_reads,
                created_at=r.created_at,
            )
        )
    return results


def get_latest_recommendation(deal_id: str, db: Session) -> Optional[RecommendationRead]:
    recs = get_recommendations_for_deal(deal_id=deal_id, db=db)
    return recs[0] if recs else None
