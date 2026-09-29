from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="SALES_REP")  # SALES_REP, SALES_MANAGER, ADMIN
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    deals: Mapped[List["Deal"]] = relationship(back_populates="owner")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    industry: Mapped[str] = mapped_column(String(120), nullable=False, default="Technology")
    size: Mapped[str] = mapped_column(String(80), nullable=False, default="Enterprise")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    contacts: Mapped[List["Contact"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    deals: Mapped[List["Deal"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped[Company] = relationship(back_populates="contacts")
    deals: Mapped[List["Deal"]] = relationship(back_populates="primary_contact")


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    primary_contact_id: Mapped[Optional[str]] = mapped_column(ForeignKey("contacts.id"), nullable=True, index=True)
    owner_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Stages: NEW, QUALIFICATION, DISCOVERY, EVALUATION, NEGOTIATION, STALLED, WON, LOST
    stage: Mapped[str] = mapped_column(String(32), nullable=False, default="NEW", index=True)
    value: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN", index=True)  # OPEN, WON, LOST, STALLED
    probability: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    expected_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company: Mapped[Company] = relationship(back_populates="deals")
    primary_contact: Mapped[Optional[Contact]] = relationship(back_populates="deals")
    owner: Mapped[Optional[User]] = relationship(back_populates="deals")
    interactions: Mapped[List["Interaction"]] = relationship(back_populates="deal", cascade="all, delete-orphan", order_by="Interaction.occurred_at.desc()")
    outcomes: Mapped[List["DealOutcome"]] = relationship(back_populates="deal", cascade="all, delete-orphan")
    recommendations: Mapped[List["Recommendation"]] = relationship(back_populates="deal", cascade="all, delete-orphan", order_by="Recommendation.created_at.desc()")


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)  # MEETING, CALL, EMAIL, NOTE
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    participants: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON encoded list of participant names
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hindsight_document_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    memory_sync_status: Mapped[str] = mapped_column(String(32), nullable=False, default="SYNCED")  # SYNCED, PENDING, FAILED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    deal: Mapped[Deal] = relationship(back_populates="interactions")
    evidences: Mapped[List["RecommendationEvidence"]] = relationship(back_populates="interaction")


class DealOutcome(Base):
    __tablename__ = "deal_outcomes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # WON, LOST, STALLED
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    strategy_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    closed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    deal: Mapped[Deal] = relationship(back_populates="outcomes")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_label: Mapped[str] = mapped_column(String(32), nullable=False, default="supported")  # supported, limited_evidence, insufficient_evidence
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    historical_pattern: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    caveats: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    deal: Mapped[Deal] = relationship(back_populates="recommendations")
    evidence: Mapped[List["RecommendationEvidence"]] = relationship(back_populates="recommendation", cascade="all, delete-orphan")


class RecommendationEvidence(Base):
    __tablename__ = "recommendation_evidence"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    recommendation_id: Mapped[str] = mapped_column(ForeignKey("recommendations.id"), nullable=False, index=True)
    interaction_id: Mapped[Optional[str]] = mapped_column(ForeignKey("interactions.id"), nullable=True, index=True)
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False, default="interaction")  # interaction, historical_deal, memory_fact
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    recommendation: Mapped[Recommendation] = relationship(back_populates="evidence")
    interaction: Mapped[Optional[Interaction]] = relationship(back_populates="evidences")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    deal_id: Mapped[Optional[str]] = mapped_column(ForeignKey("deals.id"), nullable=True, index=True)
    intent: Mapped[str] = mapped_column(String(32), nullable=False)  # FACTUAL, SUMMARY, STRATEGY, PATTERN
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    token_usage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON encoded token stats
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SUCCESS")  # SUCCESS, FAILED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(64), nullable=False)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
