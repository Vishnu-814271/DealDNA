"""Agent Orchestrator.
Direct Live LLM Reasoning Engine with Hindsight Memory Integration.
Executes 100% live AI generation with zero canned/fallback responses.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models import AgentRun, Deal, Recommendation, RecommendationEvidence
from app.modules.agents.context_builder import build_deal_context
from app.modules.agents.intent_router import classify_intent
from app.schemas import AgentChatResponse, EvidenceItem

logger = logging.getLogger("dealdna.agents.orchestrator")


class AgentOrchestrator:
    def __init__(self):
        self.openai_key = settings.openai_api_key
        self.openai_model = settings.openai_model
        self.gemini_key = settings.gemini_api_key
        self.gemini_model = settings.gemini_model
        self.groq_key = settings.groq_api_key
        self.groq_model = settings.groq_model

    def handle_chat(self, deal_id: str, message: str, db: Session) -> AgentChatResponse:
        start_time = time.time()
        intent = classify_intent(message)

        self.openai_key = settings.openai_api_key
        self.openai_model = settings.openai_model
        self.gemini_key = settings.gemini_api_key
        self.gemini_model = settings.gemini_model
        self.groq_key = settings.groq_api_key
        self.groq_model = settings.groq_model

        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        if not deal:
            return AgentChatResponse(
                answer="Error: Deal not found. Please select a valid deal.",
                intent=intent,
                latency_ms=0,
            )

        context = build_deal_context(deal=deal, db=db, query=message)

        # 1. Attempt Live Generation via OpenAI
        response, err = None, None
        if self.openai_key and not self.openai_key.startswith("change"):
            response, err = self._call_openai(context, message, deal, intent)

        # 2. If Gemini key is set, try Gemini
        if not response and self.gemini_key:
            response, err = self._call_gemini(context, message, deal, intent)

        # 3. If Groq key is set, try Groq
        if not response and self.groq_key:
            response, err = self._call_groq(context, message, deal, intent)

        # 4. If no LLM could be reached, return the explicit live error (NO canned fallback answers)
        if not response:
            error_details = err or (
                "No active LLM API key configured. Please set a valid `OPENAI_API_KEY`, `GEMINI_API_KEY`, or `GROQ_API_KEY` in `backend/.env` to enable live AI reasoning."
            )
            response = AgentChatResponse(
                answer=f"**[AI Generation Error]**\n\n{error_details}\n\n*DealDNA does not use static canned fallbacks. Please ensure your API key has active quota/credits.*",
                intent=intent,
                confidence_label="error",
                memory_count=len(context.get("memories", [])),
                evidence=[],
            )
            provider_used = "None"
            model_used = "None"
        else:
            provider_used = "Live LLM"
            model_used = self.openai_model if self.openai_key else (self.gemini_model if self.gemini_key else self.groq_model)

        latency_ms = int((time.time() - start_time) * 1000)
        response.latency_ms = latency_ms

        # Record Agent Run in database
        try:
            run = AgentRun(
                id=f"run-{uuid.uuid4().hex[:8]}",
                deal_id=deal.id,
                intent=intent,
                provider=provider_used,
                model=model_used,
                latency_ms=latency_ms,
                status="SUCCESS" if response.confidence_label != "error" else "ERROR",
            )
            db.add(run)
            db.commit()
        except Exception as e:
            logger.warning("Failed to record agent run log: %s", e)
            db.rollback()

        return response

    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        return (
            "You are DealDNA AI, an elite enterprise revenue memory and deal intelligence assistant.\n"
            "You are provided with verified Hindsight long-term memories (World Facts, Experiences, Observations), "
            "deal timeline transcripts, stakeholder roles, and historical win/loss outcomes from past accounts.\n\n"
            "Guidelines:\n"
            "1. Answer the user's specific question directly, concisely, and dynamically.\n"
            "2. Ground your reasoning in the provided deal state, retained memories, and historical comparables.\n"
            "3. Reference exact figures, stakeholders, objections, and past precedents where applicable.\n"
            "4. Structure your response with clean markdown headings and bullet points."
        )

    def _call_openai(
        self, context: Dict[str, Any], query: str, deal: Deal, intent: str
    ) -> tuple[Optional[AgentChatResponse], Optional[str]]:
        try:
            system_prompt = self._build_system_prompt(context)
            context_str = json.dumps(context, indent=2)
            user_content = f"### Deal Context & Hindsight Memories:\n{context_str}\n\n### User Question:\n{query}"

            resp = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 800,
                },
                timeout=25.0,
            )

            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                
                evidence_items = []
                for m in context.get("memories", [])[:4]:
                    if m.get("source_interaction_id"):
                        evidence_items.append(
                            EvidenceItem(
                                interaction_id=m["source_interaction_id"],
                                reason=f"Memory: {m.get('statement', '')[:80]}",
                            )
                        )

                return (
                    AgentChatResponse(
                        answer=content,
                        intent=intent,
                        confidence_label="high_confidence",
                        memory_count=len(context.get("memories", [])),
                        evidence=evidence_items,
                    ),
                    None,
                )
            elif resp.status_code == 429:
                return (None, f"OpenAI API error (HTTP 429 - Rate Limit / Quota Exceeded): Your OpenAI account has exceeded its current quota or rate limit.")
            elif resp.status_code == 401:
                return (None, f"OpenAI API error (HTTP 401 - Unauthorized): Invalid OPENAI_API_KEY.")
            else:
                return (None, f"OpenAI API error (HTTP {resp.status_code}): {resp.text[:200]}")
        except Exception as e:
            return (None, f"OpenAI connection error: {str(e)}")

    def _call_gemini(
        self, context: Dict[str, Any], query: str, deal: Deal, intent: str
    ) -> tuple[Optional[AgentChatResponse], Optional[str]]:
        try:
            system_prompt = self._build_system_prompt(context)
            context_str = json.dumps(context, indent=2)
            prompt = f"{system_prompt}\n\n### Deal Context & Memories:\n{context_str}\n\n### User Question:\n{query}"

            # Clean model name
            model_name = self.gemini_model.strip()
            if not model_name.startswith("models/"):
                model_endpoint = f"models/{model_name}"
            else:
                model_endpoint = model_name

            url = f"https://generativelanguage.googleapis.com/v1beta/{model_endpoint}:generateContent?key={self.gemini_key}"
            resp = httpx.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800},
                },
                timeout=25.0,
            )

            if resp.status_code == 200:
                data = resp.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return (
                    AgentChatResponse(
                        answer=content,
                        intent=intent,
                        confidence_label="high_confidence",
                        memory_count=len(context.get("memories", [])),
                        evidence=[],
                    ),
                    None,
                )
            elif resp.status_code == 429:
                return (None, "Google Gemini API error (HTTP 429 - Rate Limit / Quota Exceeded): Your Gemini API key has exceeded its current rate limit or quota.")
            elif resp.status_code == 404:
                return (None, f"Google Gemini API error (HTTP 404 - Model Not Found): Model '{model_name}' is not recognized or not available for this API key. Recommended model: 'gemini-1.5-flash' or 'gemini-2.5-flash'.")
            else:
                return (None, f"Google Gemini API error (HTTP {resp.status_code}): {resp.text[:200]}")
        except Exception as e:
            return (None, f"Gemini connection error: {str(e)}")

    def _call_groq(
        self, context: Dict[str, Any], query: str, deal: Deal, intent: str
    ) -> tuple[Optional[AgentChatResponse], Optional[str]]:
        try:
            system_prompt = self._build_system_prompt(context)
            context_str = json.dumps(context, indent=2)
            user_content = f"### Deal Context:\n{context_str}\n\n### User Question:\n{query}"

            resp = httpx.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.groq_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 800,
                },
                timeout=25.0,
            )

            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return (
                    AgentChatResponse(
                        answer=content,
                        intent=intent,
                        confidence_label="high_confidence",
                        memory_count=len(context.get("memories", [])),
                        evidence=[],
                    ),
                    None,
                )
            else:
                return (None, f"Groq API error (HTTP {resp.status_code}): {resp.text[:200]}")
        except Exception as e:
            return (None, f"Groq connection error: {str(e)}")


agent_orchestrator = AgentOrchestrator()
