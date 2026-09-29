"""Hindsight Memory Adapter.

Provides Retain, Recall, and Reflect operations over customer and deal memory.
Integrates with the live Hindsight service when credentials are provided,
and features a local deterministic memory engine that hydrates from DB
for offline development and hackathon demonstrations.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

from app.config import settings

logger = logging.getLogger("dealdna.memory.hindsight")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class HindsightMemoryItem:
    def __init__(
        self,
        memory_id: str,
        bank_id: str,
        deal_id: str,
        memory_type: str,  # World, Experience, Observation
        content: str,
        source_interaction_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = memory_id
        self.bank_id = bank_id
        self.deal_id = deal_id
        self.type = memory_type
        self.content = content
        self.source_interaction_id = source_interaction_id
        self.metadata = metadata or {}
        self.created_at = created_at or utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "bank_id": self.bank_id,
            "deal_id": self.deal_id,
            "type": self.type,
            "statement": self.content,
            "source_interaction_id": self.source_interaction_id,
            "confidence": self.metadata.get("confidence", 85),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class HindsightAdapter:
    def __init__(self):
        self.api_key = settings.hindsight_api_key
        self.api_url = settings.hindsight_api_url.rstrip("/")
        self.default_bank_id = settings.hindsight_bank_id
        # In-process persistent memory store
        self._local_store: Dict[str, List[HindsightMemoryItem]] = {}

    def _ensure_hydrated(self, target_bank: str, deal_id: Optional[str] = None):
        """Hydrate memory from database interactions if not already populated in this process."""
        if target_bank not in self._local_store:
            self._local_store[target_bank] = []

        existing_deal_ids = {m.deal_id for m in self._local_store[target_bank]}
        if deal_id and deal_id in existing_deal_ids:
            return

        # Query DB to hydrate interactions and outcomes
        try:
            from app.db import SessionLocal
            from app.models import Interaction, DealOutcome
            db = SessionLocal()
            try:
                query = db.query(Interaction)
                if deal_id:
                    query = query.filter(Interaction.deal_id == deal_id)
                interactions = query.all()

                for inter in interactions:
                    doc_id = inter.hindsight_document_id or f"mem-{inter.id}"
                    item = HindsightMemoryItem(
                        memory_id=doc_id,
                        bank_id=target_bank,
                        deal_id=inter.deal_id,
                        memory_type="Experience",
                        content=inter.content,
                        source_interaction_id=inter.id,
                        created_at=inter.occurred_at,
                    )
                    self._local_store[target_bank].append(item)
                    self._derive_world_and_observation_memories(
                        target_bank, inter.deal_id, inter.content, inter.id
                    )

                # Also hydrate outcomes as observations
                outcomes = db.query(DealOutcome).all()
                for oc in outcomes:
                    oc_item = HindsightMemoryItem(
                        memory_id=f"mem-{oc.id}",
                        bank_id=target_bank,
                        deal_id=oc.deal_id,
                        memory_type="Observation",
                        content=f"Deal closed {oc.status}: {oc.reason} (Strategy: {oc.strategy_used or 'N/A'})",
                        source_interaction_id=oc.id,
                        created_at=oc.closed_at,
                        metadata={"confidence": 95},
                    )
                    self._local_store[target_bank].append(oc_item)
            finally:
                db.close()
        except Exception as exc:
            logger.debug("Hydration check note: %s", exc)

    def retain(
        self,
        deal_id: str,
        content: str,
        interaction_id: Optional[str] = None,
        memory_type: str = "Experience",
        metadata: Optional[Dict[str, Any]] = None,
        bank_id: Optional[str] = None,
    ) -> str:
        """Retain an interaction or event as a persistent memory."""
        target_bank = bank_id or self.default_bank_id
        doc_id = f"mem-{uuid.uuid4().hex[:8]}"

        # Attempt live Hindsight Cloud API call if configured
        if self.api_key:
            try:
                # Format stringified metadata as required by Hindsight schema
                meta_payload = {k: str(v) for k, v in (metadata or {}).items()}
                meta_payload["deal_id"] = str(deal_id)
                meta_payload["type"] = str(memory_type)

                item_payload = {
                    "content": content,
                    "document_id": doc_id,
                    "metadata": meta_payload,
                    "tags": [deal_id, memory_type.lower()]
                }
                resp = httpx.post(
                    f"{self.api_url}/v1/default/banks/{target_bank}/memories",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={"items": [item_payload], "async": False},
                    timeout=15.0,
                )
                if resp.status_code == 200:
                    logger.info("Successfully retained memory to Hindsight Cloud bank '%s'", target_bank)
            except Exception as e:
                logger.warning("Live Hindsight retain failed (%s); persisting to local store", e)

        # In addition, maintain local store for fast querying / offline fallbacks
        if target_bank not in self._local_store:
            self._local_store[target_bank] = []

        # 1. Store the direct experience memory
        item = HindsightMemoryItem(
            memory_id=doc_id,
            bank_id=target_bank,
            deal_id=deal_id,
            memory_type=memory_type,
            content=content,
            source_interaction_id=interaction_id,
            metadata=metadata or {},
        )
        self._local_store[target_bank].append(item)

        # 2. Extract World Memory (facts, roles, mentions)
        self._derive_world_and_observation_memories(target_bank, deal_id, content, interaction_id)

        return doc_id

    def _derive_world_and_observation_memories(
        self, bank_id: str, deal_id: str, content: str, interaction_id: Optional[str]
    ):
        lower = content.lower()
        
        def append_unique(mem_item: HindsightMemoryItem):
            if bank_id not in self._local_store:
                self._local_store[bank_id] = []
            if not any(m.deal_id == mem_item.deal_id and m.content.strip().lower() == mem_item.content.strip().lower() for m in self._local_store[bank_id]):
                self._local_store[bank_id].append(mem_item)

        # Check for pricing or competitor objection
        if any(k in lower for k in ["pricing", "competitor", "expensive", "cost"]):
            obs = HindsightMemoryItem(
                memory_id=f"mem-{uuid.uuid4().hex[:8]}",
                bank_id=bank_id,
                deal_id=deal_id,
                memory_type="Observation",
                content="Customer exhibits price sensitivity and benchmarked against Competitor X; requires concrete ROI defense.",
                source_interaction_id=interaction_id,
                metadata={"confidence": 92},
            )
            append_unique(obs)

        # Check for CFO / executive stakeholder
        if any(k in lower for k in ["cfo", "finance", "anita shah"]):
            world = HindsightMemoryItem(
                memory_id=f"mem-{uuid.uuid4().hex[:8]}",
                bank_id=bank_id,
                deal_id=deal_id,
                memory_type="World",
                content="CFO (Anita Shah) is an active economic decision-maker requiring quantifiable ROI before approving contract value.",
                source_interaction_id=interaction_id,
                metadata={"confidence": 95},
            )
            append_unique(world)

        # Check for case study or customer story request
        if any(k in lower for k in ["case study", "benchmark", "story", "tco"]):
            exp = HindsightMemoryItem(
                memory_id=f"mem-{uuid.uuid4().hex[:8]}",
                bank_id=bank_id,
                deal_id=deal_id,
                memory_type="Experience",
                content="Customer explicitly requested customer case study demonstrating post-implementation value.",
                source_interaction_id=interaction_id,
                metadata={"confidence": 90},
            )
            append_unique(exp)

    def recall(
        self,
        query: str,
        deal_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10,
        bank_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Recall factual customer/deal memories matching query and deal filter."""
        target_bank = bank_id or self.default_bank_id
        self._ensure_hydrated(target_bank, deal_id)

        # Attempt live Hindsight Cloud recall if configured
        if self.api_key:
            try:
                recall_payload: Dict[str, Any] = {
                    "query": query,
                    "max_tokens": 800,
                }
                if deal_id:
                    recall_payload["tags"] = [deal_id]

                resp = httpx.post(
                    f"{self.api_url}/v1/default/banks/{target_bank}/memories/recall",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=recall_payload,
                    timeout=15.0,
                )
                if resp.status_code == 200:
                    raw_results = resp.json().get("results", [])
                    if raw_results:
                        formatted = []
                        for r in raw_results:
                            m_type = r.get("type", "experience").capitalize()
                            if memory_type and m_type.lower() != memory_type.lower():
                                continue
                            meta = r.get("metadata") or {}
                            formatted.append({
                                "id": r.get("id"),
                                "bank_id": target_bank,
                                "deal_id": meta.get("deal_id", deal_id or "DEAL-LIVE"),
                                "type": m_type,
                                "statement": r.get("text", ""),
                                "confidence": int(meta.get("confidence", 95)),
                                "entities": r.get("entities", []),
                                "score": round(float(r.get("scores", {}).get("final", 1.0)), 3),
                                "source": "hindsight_cloud",
                                "created_at": r.get("occurred_start") or r.get("mentioned_at"),
                            })
                        if formatted:
                            logger.info("Recalled %d memories from Hindsight Cloud bank '%s'", len(formatted), target_bank)
                            return formatted[:limit]
            except Exception as e:
                logger.warning("Live Hindsight recall failed (%s); using local memory engine", e)

        # Fallback to local memory engine
        memories = self._local_store.get(target_bank, [])
        results = []

        query_terms = set(query.lower().split())

        for mem in memories:
            if deal_id and mem.deal_id != deal_id:
                continue
            if memory_type and mem.type.lower() != memory_type.lower():
                continue

            content_words = set(mem.content.lower().split())
            overlap = len(query_terms.intersection(content_words))
            
            if not query_terms or overlap > 0 or len(query.strip()) <= 3:
                item_dict = mem.to_dict()
                item_dict["score"] = overlap
                results.append(item_dict)

        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return [r for r in results[:limit]]

    def reflect(
        self,
        query: str,
        deal_id: str,
        context: Optional[Dict[str, Any]] = None,
        bank_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reflect synthesizes high-level strategic reasoning over stored memories."""
        target_bank = bank_id or self.default_bank_id
        self._ensure_hydrated(target_bank, deal_id)

        # Attempt live Hindsight Cloud reflect
        if self.api_key:
            try:
                reflect_payload: Dict[str, Any] = {
                    "query": query,
                    "max_tokens": 600,
                }
                if deal_id:
                    reflect_payload["tags"] = [deal_id]

                resp = httpx.post(
                    f"{self.api_url}/v1/default/banks/{target_bank}/reflect",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json=reflect_payload,
                    timeout=20.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    reflect_text = data.get("text", "")
                    if reflect_text:
                        logger.info("Generated live Hindsight reflect synthesis for bank '%s'", target_bank)
                        return {
                            "strategic_synthesis": reflect_text,
                            "recommendation": reflect_text,
                            "confidence_label": "supported",
                            "rationale": "Synthesized directly via Hindsight AI agent reflection loop against stored deal memories.",
                            "historical_pattern": "Observed customer behavior and stakeholder requirements from live memory bank.",
                            "next_action": "Execute the recommended next step identified in the strategic synthesis.",
                            "caveats": "Continuously confirm alignment with the economic buyer as new interactions occur.",
                            "evidence": [{"interaction_id": "hsk-live", "reason": "Hindsight Memory Bank live synthesis"}],
                        }
            except Exception as e:
                logger.warning("Live Hindsight reflect failed (%s); fallback to local reasoning engine", e)

        # Local Reflect synthesis fallback
        deal_memories = [m for m in self._local_store.get(target_bank, []) if m.deal_id == deal_id]
        
        has_price_objection = any("price" in m.content.lower() or "cost" in m.content.lower() for m in deal_memories)
        has_cfo = any("cfo" in m.content.lower() or "finance" in m.content.lower() or "anita" in m.content.lower() for m in deal_memories)

        evidence_items = []
        for m in deal_memories:
            if m.source_interaction_id:
                evidence_items.append({
                    "interaction_id": m.source_interaction_id,
                    "reason": f"From memory: {m.content[:80]}...",
                })

        if not evidence_items and context and "interactions" in context:
            for inter in context["interactions"]:
                evidence_items.append({
                    "interaction_id": inter["id"],
                    "reason": f"From timeline: {inter['content'][:80]}...",
                })

        if has_price_objection and has_cfo:
            pattern = "In comparable historical deals with pricing friction and CFO involvement, deals won at an 80%+ rate when paired with an ROI memo and customer case study."
            recommendation = (
                "Prepare an executive ROI validation memo for the CFO and deliver the requested case study. "
                "Schedule a 20-minute executive walkthrough before submitting the revised commercial proposal."
            )
            next_action = "Send ROI justification model and enterprise case study to Anita Shah (CFO)."
            rationale = "Customer has raised pricing concerns relative to Competitor X and needs CFO buy-in. Historical won deals indicate pricing objections dissipate once business-value evidence is documented."
            caveats = "Avoid offering unilateral discounting before the CFO confirms understanding of total cost of ownership."
        else:
            pattern = "Early stakeholder alignment across technical and economic buyers is the primary differentiator in active pipeline progression."
            recommendation = "Engage the key economic and technical stakeholders to validate timeline and purchase criteria."
            next_action = "Schedule discovery follow-up with the primary buying committee."
            rationale = "Active interactions highlight emerging buyer interest. Establishing clear next steps prevents pipeline stagnation."
            caveats = "Ensure all decision-makers are identified early in evaluation."

        return {
            "strategic_synthesis": recommendation,
            "recommendation": recommendation,
            "confidence_label": "supported" if len(evidence_items) > 0 else "limited_evidence",
            "rationale": rationale,
            "historical_pattern": pattern,
            "next_action": next_action,
            "caveats": caveats,
            "evidence": evidence_items[:4],
        }

    def list_all_memories(self, deal_id: Optional[str] = None, bank_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return all memories for the explorer view."""
        target_bank = bank_id or self.default_bank_id
        self._ensure_hydrated(target_bank, deal_id)

        # Check live Hindsight memory bank
        if self.api_key:
            try:
                resp = httpx.get(
                    f"{self.api_url}/v1/default/banks/{target_bank}/memories/list",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    if items:
                        live_items = []
                        for it in items:
                            meta = it.get("metadata") or {}
                            d_id = meta.get("deal_id", deal_id or "DEAL-LIVE")
                            if deal_id and d_id != deal_id:
                                continue
                            live_items.append({
                                "id": it.get("id"),
                                "bank_id": target_bank,
                                "deal_id": d_id,
                                "type": it.get("type", "experience").capitalize(),
                                "statement": it.get("text", ""),
                                "confidence": int(meta.get("confidence", 95)),
                                "entities": it.get("entities", []),
                                "created_at": it.get("mentioned_at") or it.get("occurred_start"),
                            })
                        if live_items:
                            return live_items
            except Exception as e:
                logger.warning("Live Hindsight list memories failed (%s)", e)

        items = self._local_store.get(target_bank, [])
        if deal_id:
            items = [m for m in items if m.deal_id == deal_id]
        return [m.to_dict() for m in items]


hindsight_adapter = HindsightAdapter()
