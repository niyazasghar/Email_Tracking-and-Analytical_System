# automatic_followup.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from db import get_db
from models import Email, Company
from schemas.schemas import EmailOut
from typing import List

# Import for superuser requirement
from routers.auth import  get_current_active_superuser, User

router = APIRouter(prefix="/followups", tags=["Automated Follow-Ups"])

FOLLOWUP_DAYS = 3
FOLLOWUP_EMAIL = "followup@company.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-email-password"



def send_followup_email(email_record: Email, company_name: str, recipient_email: str):
    """
    Sends a follow-up email to the recipient for the email needing follow-up.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = f"Follow-up: {email_record.subject}"

        body = f"""
        Hello,

        This is a follow-up email regarding your recent correspondence about the subject: "{email_record.subject}".
        We wanted to check if you have any further queries or feedback.

        Looking forward to your response.

        Best Regards,
        {company_name}
        """
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            text = msg.as_string()
            server.sendmail(SENDER_EMAIL, recipient_email, text)
            print(f"Follow-up email sent to {recipient_email}")
    except Exception as e:
        print(f"Error sending follow-up email: {e}")


@router.post("/run", response_model=List[EmailOut], dependencies=[Depends(get_current_active_superuser)])
def run_automated_followups(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Checks for emails older than FOLLOWUP_DAYS that are still "Sent"
    and updates them to "Follow-up Required" or sends a follow-up email automatically.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=FOLLOWUP_DAYS)
    emails_to_follow_up = db.query(Email).filter(
        Email.status == "Sent",
        Email.sent_timestamp < cutoff_date
    ).all()

    updated_emails = []

    for email_record in emails_to_follow_up:
        company = db.query(Company).filter(Company.company_id == email_record.company_id).first()
        if not company:
            continue

        if company.domain == "example.com":
            recipient_email = FOLLOWUP_EMAIL
        else:
            recipient_email = email_record.recipient

        background_tasks.add_task(send_followup_email, email_record, company.company_name, recipient_email)

        email_record.status = "Follow-up Required"
        db.commit()
        db.refresh(email_record)
        updated_emails.append(email_record)

    return updated_emails
