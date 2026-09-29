from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.deals.service import (
    add_interaction,
    create_deal,
    get_deal,
    get_deal_patterns,
    get_deal_timeline,
    list_deals,
    record_deal_outcome,
    update_deal,
)
from app.modules.memory.service import get_memories_for_deal
from app.modules.recommendations.service import get_recommendations_for_deal
from app.modules.agents.orchestrator import agent_orchestrator
from app.schemas import (
    AgentChatResponse,
    DealCreate,
    DealOutcomeCreate,
    DealOutcomeRead,
    DealPatternRead,
    DealRead,
    DealUpdate,
    InteractionCreate,
    InteractionRead,
    MemoryItemRead,
    RecommendationRead,
)

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=List[DealRead])
def read_deals(db: Session = Depends(get_db)) -> List[DealRead]:
    return list_deals(db)


@router.post("", response_model=DealRead, status_code=status.HTTP_201_CREATED)
def create_new_deal(payload: DealCreate, db: Session = Depends(get_db)) -> DealRead:
    return create_deal(payload, db)


@router.get("/{deal_id}", response_model=DealRead)
def read_deal(deal_id: str, db: Session = Depends(get_db)) -> DealRead:
    deal = get_deal(deal_id, db)
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return deal


@router.patch("/{deal_id}", response_model=DealRead)
def modify_deal(deal_id: str, payload: DealUpdate, db: Session = Depends(get_db)) -> DealRead:
    deal = update_deal(deal_id, payload, db)
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return deal


@router.get("/{deal_id}/timeline", response_model=List[InteractionRead])
def read_deal_timeline(deal_id: str, db: Session = Depends(get_db)) -> List[InteractionRead]:
    return get_deal_timeline(deal_id, db)


@router.post("/{deal_id}/interactions", response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
def post_interaction(
    deal_id: str, payload: InteractionCreate, db: Session = Depends(get_db)
) -> InteractionRead:
    try:
        return add_interaction(deal_id, payload, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{deal_id}/memories", response_model=List[MemoryItemRead])
def read_deal_memories(deal_id: str) -> List[MemoryItemRead]:
    return get_memories_for_deal(deal_id)


@router.get("/{deal_id}/patterns", response_model=DealPatternRead)
def read_deal_patterns(deal_id: str, db: Session = Depends(get_db)) -> DealPatternRead:
    return get_deal_patterns(deal_id, db)


@router.post("/{deal_id}/outcome", response_model=DealOutcomeRead, status_code=status.HTTP_201_CREATED)
def post_deal_outcome(
    deal_id: str, payload: DealOutcomeCreate, db: Session = Depends(get_db)
) -> DealOutcomeRead:
    try:
        return record_deal_outcome(deal_id, payload, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{deal_id}/analyze", response_model=AgentChatResponse)
def analyze_deal(deal_id: str, db: Session = Depends(get_db)) -> AgentChatResponse:
    return agent_orchestrator.handle_chat(
        deal_id=deal_id,
        message="What should I do next to progress this deal?",
        db=db,
    )


@router.get("/{deal_id}/recommendations", response_model=List[RecommendationRead])
def read_recommendations(deal_id: str, db: Session = Depends(get_db)) -> List[RecommendationRead]:
    return get_recommendations_for_deal(deal_id, db)
