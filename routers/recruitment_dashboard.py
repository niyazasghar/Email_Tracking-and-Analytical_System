# routers/recruitment.py
from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from typing import List

from db import get_db
from models import Company, RecruitmentEvent, Placement
from schemas.schemas import (
    CompanyCreate, CompanyMinimal,  # ← new minimal schema
    RecruitmentEventCreate, RecruitmentEventOut,
    PlacementCreate, PlacementOut, UpcomingRecruitmentOut
)
from routers.auth import (
    get_current_user,
    get_current_active_superuser,
    User,
)

router = APIRouter(prefix="/recruitment", tags=["Recruitment Dashboard"])

# ─────────────────────────────────────────────────────────────
# 1)  LIST COMPANIES  (for dropdowns, etc.)
# ─────────────────────────────────────────────────────────────
@router.get(
    "/companies",
    response_model=List[CompanyMinimal],         # ← only id & name required
    dependencies=[Depends(get_current_user)]
)
def list_companies(db: Session = Depends(get_db)):
    """
    Minimal company list → [{company_id, company_name}, …]
    """
    return db.query(Company).order_by(Company.company_name).all()


# ─────────────────────────────────────────────────────────────
# 2)  UPCOMING RECRUITERS  (by recruitment_year)
# ─────────────────────────────────────────────────────────────
@router.get(
    "/upcoming",
    response_model=List[UpcomingRecruitmentOut],
    dependencies=[Depends(get_current_user)]
)
def get_upcoming_recruitment(
    year: int = Query(..., description="Filter by recruitment_year, e.g. 2025"),
    db: Session = Depends(get_db)
):
    """
    Returns all recruitment events plus their company details
    for companies whose recruitment_year == `year`.
    """
    # Join Company → RecruitmentEvent
    rows = (
        db.query(Company, RecruitmentEvent)
          .join(RecruitmentEvent, RecruitmentEvent.company_id == Company.company_id)
          .filter(Company.recruitment_year == year)
          .order_by(Company.company_name)
          .all()
    )

    # If you want an empty list instead of 404 when none found, just return []
    results = []
    for comp, event in rows:
        results.append({
            "company_id": comp.company_id,
            "company_name": comp.company_name,
            "domain": comp.domain,
            "eligibility_criteria": comp.eligibility_criteria,
            "selection_process": comp.selection_process,
            "package_offered": comp.package_offered,
            "recruitment_year": comp.recruitment_year,
            "role_offered": comp.role_offered,
            "joining_date": comp.joining_date,
            "job_type": comp.job_type,
            "location": comp.location,
            "work_environment": comp.work_environment,
            "recruitment_mode": comp.recruitment_mode,
            "event_id": event.event_id,
            "event_date": event.event_date,
        })
    return results

# ─────────────────────────────────────────────────────────────
# 3)  ADD COMPANY  (superuser)
# ─────────────────────────────────────────────────────────────
@router.post(
    "/company",
    response_model=CompanyMinimal,
    dependencies=[Depends(get_current_active_superuser)]
)
def add_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    # avoid duplicates for same domain + year
    exists = (
        db.query(Company)
        .filter(
            Company.domain == payload.domain,
            Company.recruitment_year == payload.recruitment_year,
        )
        .first()
    )
    if exists:
        raise HTTPException(
            400, "Company with this domain for that recruitment year already exists."
        )

    company = Company(**payload.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


# ─────────────────────────────────────────────────────────────
# 4)  ADD RECRUITMENT EVENT  (any logged‑in user)
# ─────────────────────────────────────────────────────────────
@router.post(
    "/event",
    response_model=RecruitmentEventOut,
    dependencies=[Depends(get_current_user)]
)
def add_recruitment_event(
    payload: RecruitmentEventCreate,
    db: Session = Depends(get_db),
):
    comp = db.get(Company, payload.company_id)
    if not comp:
        raise HTTPException(404, "Company not found.")

    event = RecruitmentEvent(**payload.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# ─────────────────────────────────────────────────────────────
# 5)  ADD PLACED STUDENT  (superuser)
# ─────────────────────────────────────────────────────────────
@router.post(
    "/add-student",
    response_model=PlacementOut,
    dependencies=[Depends(get_current_active_superuser)]
)
def add_placed_student(payload: PlacementCreate, db: Session = Depends(get_db)):
    comp = db.get(Company, payload.company_id)
    if not comp:
        raise HTTPException(404, "Company not found.")

    placement = Placement(**payload.dict())
    db.add(placement)
    db.commit()
    db.refresh(placement)

    # enrich with company_name for output model
    placement.company_name = comp.company_name
    return placement
