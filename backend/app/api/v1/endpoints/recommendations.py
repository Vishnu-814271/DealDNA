from fastapi import APIRouter

from app.modules.recommendations.service import get_recommendations_for_deal
from app.schemas import RecommendationRead

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendationRead])
def read_recommendations() -> list[RecommendationRead]:
    return [
        item
        for deal_id in ["deal-1001", "deal-1002", "deal-1003"]
        for item in get_recommendations_for_deal(deal_id)
    ]


@router.get("/{deal_id}", response_model=list[RecommendationRead])
def read_recommendations_for_deal(deal_id: str) -> list[RecommendationRead]:
    return get_recommendations_for_deal(deal_id)
