"""Seed Demo Data script for DealDNA.
Seeds Acme Technologies (DEAL-1007) and historical comparable deals with outcomes and Hindsight memories,
matching SDD Section 28 & 15.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine
from app.models import (
    Company,
    Contact,
    Deal,
    DealOutcome,
    Interaction,
    User,
)
from app.modules.memory.hindsight_adapter import hindsight_adapter


def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Company).filter(Company.id == "comp-acme").first():
            print("Database already contains demo seed data.")
            return

        print("Seeding DealDNA database with hackathon demo scenario...")

        # 1. Users
        rep = User(
            id="user-rep-1",
            name="Sarah Jenkins",
            email="sarah.jenkins@dealdna.internal",
            role="SALES_REP",
        )
        db.add(rep)

        # 2. Target Account: Acme Technologies (DEAL-1007)
        comp_acme = Company(
            id="comp-acme",
            name="Acme Technologies",
            industry="Software & Cloud Services",
            size="Enterprise (2,500 employees)",
        )
        db.add(comp_acme)

        contact_raj = Contact(
            id="cont-raj",
            company_id="comp-acme",
            name="Raj Mehta",
            role="VP of Procurement",
            email="raj.mehta@acmetechnologies.com",
            phone="+1 (555) 234-8901",
        )
        contact_anita = Contact(
            id="cont-anita",
            company_id="comp-acme",
            name="Anita Shah",
            role="Chief Financial Officer (CFO)",
            email="anita.shah@acmetechnologies.com",
            phone="+1 (555) 234-8902",
        )
        db.add_all([contact_raj, contact_anita])

        deal_acme = Deal(
            id="DEAL-1007",
            company_id="comp-acme",
            primary_contact_id="cont-raj",
            owner_id="user-rep-1",
            name="Acme Enterprise Platform Expansion",
            stage="EVALUATION",
            value=Decimal("175000.00"),
            currency="USD",
            status="OPEN",
            probability=65,
            expected_close_date=datetime.utcnow() + timedelta(days=30),
            summary="Acme is evaluating DealDNA to streamline revenue context. Pricing objection raised relative to Competitor X; CFO needs ROI validation.",
        )
        db.add(deal_acme)
        db.commit()

        # Seed Acme's 3 interactions from SDD Section 28
        now = datetime.utcnow()
        int1 = Interaction(
            id="int-acme-1",
            deal_id="DEAL-1007",
            type="MEETING",
            occurred_at=now - timedelta(days=6),
            participants='["Raj Mehta", "Sarah Jenkins"]',
            content="We are interested, but your pricing is higher than Competitor X.",
            summary="Competitor pricing objection raised by procurement.",
            hindsight_document_id="mem-acme-int-1",
            memory_sync_status="SYNCED",
        )
        int2 = Interaction(
            id="int-acme-2",
            deal_id="DEAL-1007",
            type="CALL",
            occurred_at=now - timedelta(days=3),
            participants='["Anita Shah", "Sarah Jenkins"]',
            content="Our CFO needs to understand ROI before allocating budget for Q4.",
            summary="CFO requires quantitative ROI model.",
            hindsight_document_id="mem-acme-int-2",
            memory_sync_status="SYNCED",
        )
        int3 = Interaction(
            id="int-acme-3",
            deal_id="DEAL-1007",
            type="EMAIL",
            occurred_at=now - timedelta(days=1),
            participants='["Raj Mehta", "Sarah Jenkins"]',
            content="Send us a relevant case study showing similar companies succeeding with this approach.",
            summary="Request for customer case study / benchmark.",
            hindsight_document_id="mem-acme-int-3",
            memory_sync_status="SYNCED",
        )
        db.add_all([int1, int2, int3])
        db.commit()

        # Retain Acme's interactions in Hindsight Memory
        hindsight_adapter.retain(
            deal_id="DEAL-1007",
            content="We are interested, but your pricing is higher than Competitor X.",
            interaction_id="int-acme-1",
            memory_type="Experience",
            metadata={"participants": ["Raj Mehta"], "type": "MEETING"},
        )
        hindsight_adapter.retain(
            deal_id="DEAL-1007",
            content="Our CFO needs to understand ROI before allocating budget for Q4.",
            interaction_id="int-acme-2",
            memory_type="Experience",
            metadata={"participants": ["Anita Shah"], "type": "CALL"},
        )
        hindsight_adapter.retain(
            deal_id="DEAL-1007",
            content="Send us a relevant case study showing similar companies succeeding with this approach.",
            interaction_id="int-acme-3",
            memory_type="Experience",
            metadata={"participants": ["Raj Mehta"], "type": "EMAIL"},
        )

        # 3. Seed Historical Comparable Deals with Outcomes
        comp_globex = Company(
            id="comp-globex",
            name="Globex International",
            industry="Enterprise Software",
            size="Enterprise (5,000 employees)",
        )
        deal_globex = Deal(
            id="DEAL-1002",
            company_id="comp-globex",
            owner_id="user-rep-1",
            name="Globex Global License",
            stage="WON",
            value=Decimal("320000.00"),
            currency="USD",
            status="WON",
            probability=100,
            summary="Globex initially balked at Competitor X pricing. Deal closed after presenting CFO with detailed ROI analysis.",
        )
        outcome_globex = DealOutcome(
            id="out-globex",
            deal_id="DEAL-1002",
            status="WON",
            reason="Delivered customized ROI spreadsheet and case study directly to CFO.",
            strategy_used="CFO ROI memo + executive walkthrough",
            closed_at=now - timedelta(days=45),
        )

        comp_initech = Company(
            id="comp-initech",
            name="Initech Financial Solutions",
            industry="Fintech",
            size="Mid-Market (800 employees)",
        )
        deal_initech = Deal(
            id="DEAL-1003",
            company_id="comp-initech",
            owner_id="user-rep-1",
            name="Initech Core Integration",
            stage="WON",
            value=Decimal("185000.00"),
            currency="USD",
            status="WON",
            probability=100,
            summary="Customer hesitated over price differential. Closed after providing fintech peer case study.",
        )
        outcome_initech = DealOutcome(
            id="out-initech",
            deal_id="DEAL-1003",
            status="WON",
            reason="Provided relevant benchmark case study demonstrating 4x payback.",
            strategy_used="Peer case study + quantified payback period",
            closed_at=now - timedelta(days=70),
        )

        comp_cyberdyne = Company(
            id="comp-cyberdyne",
            name="Cyberdyne Systems",
            industry="Robotics & AI",
            size="Enterprise (1,800 employees)",
        )
        deal_cyberdyne = Deal(
            id="DEAL-1004",
            company_id="comp-cyberdyne",
            owner_id="user-rep-1",
            name="Cyberdyne Systems License",
            stage="LOST",
            value=Decimal("210000.00"),
            currency="USD",
            status="LOST",
            probability=0,
            summary="Customer chose Competitor X after sales team offered standard 10% discount without proving ROI to executive buyer.",
        )
        outcome_cyberdyne = DealOutcome(
            id="out-cyberdyne",
            deal_id="DEAL-1004",
            status="LOST",
            reason="Discounting alone failed to convince the CFO; Competitor X won on perceived value.",
            strategy_used="Unit discounting without economic ROI justification",
            closed_at=now - timedelta(days=90),
        )

        db.add_all([
            comp_globex, deal_globex, outcome_globex,
            comp_initech, deal_initech, outcome_initech,
            comp_cyberdyne, deal_cyberdyne, outcome_cyberdyne,
        ])
        db.commit()

        # Retain outcomes in Hindsight
        hindsight_adapter.retain(
            deal_id="DEAL-1002",
            content="Globex deal WON ($320k): Pricing objection against Competitor X resolved by presenting CFO ROI model and customer case study.",
            interaction_id="out-globex",
            memory_type="Observation",
            metadata={"status": "WON", "competitor": "Competitor X"},
        )
        hindsight_adapter.retain(
            deal_id="DEAL-1003",
            content="Initech deal WON ($185k): Peer case study showing 4x payback overcame pricing hesitation in procurement.",
            interaction_id="out-initech",
            memory_type="Observation",
            metadata={"status": "WON"},
        )
        hindsight_adapter.retain(
            deal_id="DEAL-1004",
            content="Cyberdyne deal LOST ($210k): Offering discounts without CFO ROI justification caused deal to slip to Competitor X.",
            interaction_id="out-cyberdyne",
            memory_type="Observation",
            metadata={"status": "LOST", "competitor": "Competitor X"},
        )

        print("Hackathon demo scenario seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
