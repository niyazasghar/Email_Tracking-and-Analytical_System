from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import get_db
from models import Email, Company
from schemas.schemas import EmailOut, EmailOut2
from datetime import datetime
from typing import Optional, List, Dict, Any

# Require superuser
from routers.auth import get_current_active_superuser

router = APIRouter(prefix="/status", tags=["Status Management"])


def auto_update_status(email: Email) -> str:
    """
    Automatically updates the status of the email based on business logic.
    """
    # For example: If more than 3 days since it was sent, change to "Follow-up Required".
    if email.status == "Sent" and (datetime.utcnow() - email.sent_timestamp).days > 3:
        return "Follow-up Required"
    return email.status


@router.put("/update/{email_id}", response_model=EmailOut2, dependencies=[Depends(get_current_active_superuser)])
def update_status(email_id: int, new_status: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Update the status of a particular Email by its ID.
    If new_status is not provided, it will use auto_update_status logic.
    """
    email_record = db.query(Email).filter(Email.email_id == email_id).first()
    if not email_record:
        raise HTTPException(status_code=404, detail="Email not found.")

    if not new_status:
        new_status = auto_update_status(email_record)

    email_record.status = new_status
    db.commit()
    db.refresh(email_record)
    return email_record


@router.get("/company/{company_id}/status", response_model=dict, dependencies=[Depends(get_current_active_superuser)])
def get_email_status_by_company(
    company_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Returns total count of "Pending" and "Follow-up Required" emails for a specific company
    within a specific time period.
    """
    query = db.query(Email).filter(Email.company_id == company_id)

    if start_date:
        query = query.filter(Email.sent_timestamp >= start_date)
    if end_date:
        query = query.filter(Email.sent_timestamp <= end_date)

    pending_count = query.filter(Email.status == "Sent").count()
    follow_up_count = query.filter(Email.status == "Follow-up Required").count()

    return {
        "company_id": company_id,
        "pending_emails": pending_count,
        "follow_up_emails": follow_up_count
    }


@router.get("/companies", dependencies=[Depends(get_current_active_superuser)])
def get_companies(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Returns a list of all companies with ID and name.
    """
    companies = db.query(Company.company_id, Company.company_name).all()
    result = []
    for c_id, c_name in companies:
        result.append({"company_id": c_id, "company_name": c_name})
    return result


@router.get("/company/{company_id}/emails", dependencies=[Depends(get_current_active_superuser)])
def get_company_emails(company_id: int, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Returns a list of email_id, subject, and status for the given company.
    """
    emails = db.query(Email).filter(Email.company_id == company_id).all()
    result = []
    for e in emails:
        result.append({
            "email_id": e.email_id,
            "subject": e.subject,
            "status": e.status
        })
    return result
