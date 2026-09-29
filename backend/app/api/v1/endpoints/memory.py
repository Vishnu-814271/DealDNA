from typing import List, Optional
from fastapi import APIRouter, Query

from app.modules.memory.service import get_memories_for_deal, list_all_memories
from app.schemas import MemoryItemRead

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=List[MemoryItemRead])
def read_all_memories(
    deal_id: Optional[str] = Query(None)
) -> List[MemoryItemRead]:
    if deal_id:
        return get_memories_for_deal(deal_id)
    return list_all_memories()
