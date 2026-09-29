from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.modules.memory.hindsight_adapter import hindsight_adapter
from app.schemas import MemoryItemRead


def retain_interaction_memory(
    deal_id: str,
    content: str,
    interaction_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Store interaction in Hindsight and return document reference."""
    return hindsight_adapter.retain(
        deal_id=deal_id,
        content=content,
        interaction_id=interaction_id,
        memory_type="Experience",
        metadata=metadata,
    )


def recall_memories(
    query: str,
    deal_id: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Recall factual memories matching the query."""
    return hindsight_adapter.recall(query=query, deal_id=deal_id, limit=limit)


def reflect_on_deal(
    query: str,
    deal_id: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Perform strategic reflection on deal memories."""
    return hindsight_adapter.reflect(query=query, deal_id=deal_id, context=context)


def get_memories_for_deal(deal_id: str) -> List[MemoryItemRead]:
    """Retrieve all memories retained for a deal for the Memory Explorer."""
    raw_memories = hindsight_adapter.list_all_memories(deal_id=deal_id)
    return [
        MemoryItemRead(
            id=item["id"],
            deal_id=item["deal_id"],
            type=item["type"],
            statement=item["statement"],
            source_interaction_id=item.get("source_interaction_id"),
            confidence=item.get("confidence", 85),
        )
        for item in raw_memories
    ]


def list_all_memories() -> List[MemoryItemRead]:
    """Retrieve all memories across all deals."""
    raw_memories = hindsight_adapter.list_all_memories()
    return [
        MemoryItemRead(
            id=item["id"],
            deal_id=item["deal_id"],
            type=item["type"],
            statement=item["statement"],
            source_interaction_id=item.get("source_interaction_id"),
            confidence=item.get("confidence", 85),
        )
        for item in raw_memories
    ]
