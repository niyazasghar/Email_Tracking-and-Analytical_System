# app/routers/email_tracking.py
import smtplib
import uuid
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from db import get_db
from models import Email, Company
from schemas.schemas import (
    EmailCreate,
    EmailOut,
    EmailOut1,
    CompanyMinimal
)
from routers.auth import get_current_active_superuser, get_current_user

router = APIRouter(prefix="/email-tracking", tags=["Email Tracking"])


def extract_domain(email_address: str) -> str:
    match = re.search(r"@([\w\.-]+)$", email_address)
    return match.group(1) if match else ""


def send_smtp_email(
    sender: str,
    recipient: str,
    subject: str,
    body: str,
    smtp_config: dict,
    message_id: str
):
    """
    Sends an email via SMTP (with TLS).
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg["Message-ID"] = message_id
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            server.starttls()
            server.login(smtp_config["username"], smtp_config["password"])
            server.sendmail(sender, recipient, msg.as_string())
            print(f"Sent to {recipient} (ID: {message_id})")
    except Exception as e:
        print(f"SMTP error: {e}")


@router.post(
    "/send",
    response_model=EmailOut,
    dependencies=[Depends(get_current_active_superuser)]
)
def send_email_endpoint(
    email_data: EmailCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Superuser-only: send an email via SMTP and record it.
    """
    domain = extract_domain(email_data.recipient)
    company = db.query(Company).filter(Company.domain == domain).first()

    # Auto-create company if unknown, filling all NOT NULL fields
    if not company:
        company = Company(
            company_name=domain.split(".")[0],
            domain=domain,
            eligibility_criteria="N/A",
            selection_process="N/A",
            package_offered="N/A",
            recruitment_year=datetime.utcnow().year,
            role_offered="N/A",
            job_type="N/A",
            joining_date=None,
            location=None,
            work_environment=None,
            recruitment_mode=None,
        )
        db.add(company)
        db.commit()
        db.refresh(company)

    msg_id = f"<{uuid.uuid4()}@{domain}>"
    record = Email(
        sender=email_data.sender,
        recipient=email_data.recipient,
        subject=email_data.subject,
        body=email_data.body,
        sent_timestamp=datetime.utcnow(),
        status="Sent",
        domain=domain,
        company_id=company.company_id,
        message_id=msg_id
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Example Gmail SMTP config (replace with yours!)
    smtp_conf = {
        "host": "smtp.gmail.com",
        "port": 587,
        "username": "YOUR_USER@gmail.com",
        "password": "YOUR_APP_PASSWORD"
    }

    background_tasks.add_task(
        send_smtp_email,
        email_data.sender,
        email_data.recipient,
        email_data.subject,
        email_data.body or "",
        smtp_conf,
        msg_id
    )
    return record


@router.get(
    "/companies",
    response_model=List[CompanyMinimal],
    dependencies=[Depends(get_current_user)]
)
def list_companies(db: Session = Depends(get_db)):
    """
    Any authenticated user: fetch minimal company list for dropdown.
    """
    return (
        db.query(Company)
          .order_by(Company.company_name)
          .all()
    )


@router.get(
    "/chat",
    response_model=List[EmailOut1],
    dependencies=[Depends(get_current_user)]
)
def get_email_chat(
    company_id: int = Query(..., description="Company to load chat for"),
    start_date: Optional[datetime] = Query(None),
    end_date:   Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Stream all emails for a given company (and optional date range),
    sorted ascending by sent_timestamp.
    """
    q = db.query(Email).filter(Email.company_id == company_id)
    if start_date:
        q = q.filter(Email.sent_timestamp >= start_date)
    if end_date:
        q = q.filter(Email.sent_timestamp <= end_date)
    return q.order_by(Email.sent_timestamp.asc()).all()
