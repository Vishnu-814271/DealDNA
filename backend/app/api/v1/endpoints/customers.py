from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.customers.service import (
    create_company,
    create_contact,
    get_company,
    list_companies,
    list_contacts,
)
from app.schemas import CompanyCreate, CompanyRead, ContactCreate, ContactRead

router = APIRouter(tags=["companies", "contacts"])


@router.get("/companies", response_model=List[CompanyRead])
def read_companies(db: Session = Depends(get_db)) -> List[CompanyRead]:
    return list_companies(db)


@router.post("/companies", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_new_company(payload: CompanyCreate, db: Session = Depends(get_db)) -> CompanyRead:
    return create_company(payload, db)


@router.get("/companies/{company_id}", response_model=CompanyRead)
def read_single_company(company_id: str, db: Session = Depends(get_db)) -> CompanyRead:
    company = get_company(company_id, db)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.get("/contacts", response_model=List[ContactRead])
def read_contacts(
    company_id: Optional[str] = Query(None), db: Session = Depends(get_db)
) -> List[ContactRead]:
    return list_contacts(company_id, db)


@router.post("/contacts", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_new_contact(payload: ContactCreate, db: Session = Depends(get_db)) -> ContactRead:
    return create_contact(payload, db)
