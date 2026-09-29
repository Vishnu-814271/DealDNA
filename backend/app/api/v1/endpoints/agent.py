from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.agents.orchestrator import agent_orchestrator
from app.schemas import AgentChatRequest, AgentChatResponse

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
def chat_with_agent(
    payload: AgentChatRequest, db: Session = Depends(get_db)
) -> AgentChatResponse:
    if not payload.deal_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="deal_id is required")
    if not payload.message:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="message cannot be empty")
        
    return agent_orchestrator.handle_chat(
        deal_id=payload.deal_id,
        message=payload.message,
        db=db,
    )
