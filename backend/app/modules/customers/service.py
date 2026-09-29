from __future__ import annotations

import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import Company, Contact
from app.schemas import CompanyCreate, CompanyRead, ContactCreate, ContactRead


def list_companies(db: Session) -> List[CompanyRead]:
    companies = db.query(Company).order_by(Company.name.asc()).all()
    return [CompanyRead.model_validate(c) for c in companies]


def get_company(company_id: str, db: Session) -> Optional[CompanyRead]:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return None
    return CompanyRead.model_validate(company)


def create_company(payload: CompanyCreate, db: Session) -> CompanyRead:
    comp_id = payload.id or f"comp-{uuid.uuid4().hex[:8]}"
    company = Company(
        id=comp_id,
        name=payload.name,
        industry=payload.industry,
        size=payload.size,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return CompanyRead.model_validate(company)


def list_contacts(company_id: Optional[str], db: Session) -> List[ContactRead]:
    query = db.query(Contact)
    if company_id:
        query = query.filter(Contact.company_id == company_id)
    contacts = query.order_by(Contact.name.asc()).all()
    return [ContactRead.model_validate(c) for c in contacts]


def create_contact(payload: ContactCreate, db: Session) -> ContactRead:
    cont_id = payload.id or f"cont-{uuid.uuid4().hex[:8]}"
    contact = Contact(
        id=cont_id,
        company_id=payload.company_id,
        name=payload.name,
        role=payload.role,
        email=payload.email,
        phone=payload.phone,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return ContactRead.model_validate(contact)
