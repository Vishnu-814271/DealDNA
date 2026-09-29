from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ----------------- User Schemas -----------------
class UserBase(BaseModel):
    name: str
    email: str
    role: str = "SALES_REP"
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    id: Optional[str] = None


class UserRead(UserBase):
    id: str
    created_at: Optional[datetime] = None


# ----------------- Company Schemas -----------------
class CompanyBase(BaseModel):
    name: str
    industry: str = "Technology"
    size: str = "Enterprise"
    model_config = ConfigDict(from_attributes=True)


class CompanyCreate(CompanyBase):
    id: Optional[str] = None


class CompanyRead(CompanyBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ----------------- Contact Schemas -----------------
class ContactBase(BaseModel):
    company_id: str
    name: str
    role: str
    email: str
    phone: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ContactCreate(ContactBase):
    id: Optional[str] = None


class ContactRead(ContactBase):
    id: str
    created_at: Optional[datetime] = None


# ----------------- Interaction Schemas -----------------
class InteractionBase(BaseModel):
    deal_id: str
    type: Literal["MEETING", "CALL", "EMAIL", "NOTE"] = "MEETING"
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    participants: List[str] = Field(default_factory=list)
    content: str
    summary: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class InteractionCreate(BaseModel):
    type: Literal["MEETING", "CALL", "EMAIL", "NOTE"] = "MEETING"
    occurred_at: Optional[datetime] = None
    participants: List[str] = Field(default_factory=list)
    content: str
    summary: Optional[str] = None


class InteractionRead(BaseModel):
    id: str
    deal_id: str
    type: str
    occurred_at: datetime
    participants: List[str]
    content: str
    summary: Optional[str] = None
    hindsight_document_id: Optional[str] = None
    memory_sync_status: str = "SYNCED"
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ----------------- Deal Outcome Schemas -----------------
class DealOutcomeBase(BaseModel):
    status: Literal["WON", "LOST", "STALLED"]
    reason: str
    strategy_used: Optional[str] = None
    closed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class DealOutcomeCreate(DealOutcomeBase):
    pass


class DealOutcomeRead(DealOutcomeBase):
    id: str
    deal_id: str
    created_at: Optional[datetime] = None


# ----------------- Recommendation & Evidence Schemas -----------------
class RecommendationEvidenceRead(BaseModel):
    id: Optional[str] = None
    interaction_id: Optional[str] = None
    evidence_type: str = "interaction"
    reason: str
    model_config = ConfigDict(from_attributes=True)


class RecommendationRead(BaseModel):
    id: str
    deal_id: str
    query: str
    recommendation: str
    confidence_label: Literal["supported", "limited_evidence", "insufficient_evidence"] = "supported"
    rationale: str
    historical_pattern: Optional[str] = None
    next_action: Optional[str] = None
    caveats: Optional[str] = None
    evidence: List[RecommendationEvidenceRead] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


# ----------------- Deal Schemas -----------------
DealStageType = Literal[
    "NEW",
    "QUALIFICATION",
    "DISCOVERY",
    "EVALUATION",
    "NEGOTIATION",
    "STALLED",
    "WON",
    "LOST",
]


class DealBase(BaseModel):
    company_id: str
    primary_contact_id: Optional[str] = None
    owner_id: Optional[str] = None
    name: str
    stage: DealStageType = "NEW"
    value: Decimal = Field(default=Decimal("0.0"))
    currency: str = "USD"
    status: str = "OPEN"
    probability: int = Field(default=50, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    summary: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DealCreate(DealBase):
    id: Optional[str] = None


class DealUpdate(BaseModel):
    name: Optional[str] = None
    stage: Optional[DealStageType] = None
    value: Optional[Decimal] = None
    probability: Optional[int] = Field(default=None, ge=0, le=100)
    status: Optional[str] = None
    summary: Optional[str] = None
    expected_close_date: Optional[datetime] = None


class DealRead(DealBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    company: Optional[CompanyRead] = None
    primary_contact: Optional[ContactRead] = None
    owner: Optional[UserRead] = None
    outcomes: List[DealOutcomeRead] = Field(default_factory=list)


# ----------------- Agent & Memory Schemas -----------------
class AgentChatRequest(BaseModel):
    deal_id: str
    message: str


class EvidenceItem(BaseModel):
    interaction_id: Optional[str] = None
    reason: str


class AgentChatResponse(BaseModel):
    answer: str
    recommendation: Optional[str] = None
    confidence_label: Optional[str] = "supported"
    rationale: Optional[str] = None
    historical_pattern: Optional[str] = None
    next_action: Optional[str] = None
    caveats: Optional[str] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)
    memory_count: int = 0
    intent: Literal["FACTUAL", "SUMMARY", "STRATEGY", "PATTERN"] = "STRATEGY"
    latency_ms: int = 0


class MemoryItemRead(BaseModel):
    id: str
    deal_id: str
    type: Literal["World", "Experience", "Observation"]
    statement: str
    source_interaction_id: Optional[str] = None
    confidence: int = 80
    created_at: Optional[datetime] = None


class HistoricalDealMatch(BaseModel):
    deal_id: str
    deal_name: str
    company_name: str
    outcome: str
    similarity_reason: str
    strategy_used: Optional[str] = None
    value: float = 0.0


class DealPatternRead(BaseModel):
    deal_id: str
    observed_pattern: str
    confidence_label: str
    comparable_deals: List[HistoricalDealMatch] = Field(default_factory=list)
    recommended_tactics: List[str] = Field(default_factory=list)


class ErrorEnvelope(BaseModel):
    error_code: str
    message: str
    correlation_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
