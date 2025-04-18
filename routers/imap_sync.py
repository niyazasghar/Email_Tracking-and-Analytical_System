# imap_syn.py
import imaplib
import email
import email.utils
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from db import get_db
from models import Email
import re

# Require superuser
from routers.auth import  get_current_active_superuser, User

IMAP_HOST = "imap.gmail.com"
IMAP_USER = "demo@gmail.com"
IMAP_PASS = "demo_password"



router = APIRouter()

def extract_domain(address: str) -> str:
    pattern = r"@([\w\.-]+)$"
    match = re.search(pattern, address)
    return match.group(1) if match else ""


def connect_to_imap():
    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(IMAP_USER, IMAP_PASS)
    mail.select("INBOX")
    return mail


def parse_email_message(raw_data: bytes) -> dict:
    msg = email.message_from_bytes(raw_data)

    raw_subject, raw_encoding = decode_header(msg["Subject"])[0] if msg["Subject"] else (None, None)
    if isinstance(raw_subject, bytes):
        subject = raw_subject.decode(raw_encoding if raw_encoding else "utf-8", errors="replace")
    else:
        subject = raw_subject or ""

    from_ = msg.get("From", "")
    sender = email.utils.parseaddr(from_)[1]
    recipient = email.utils.parseaddr(msg.get("To", ""))[1]
    message_id = msg.get("Message-ID")
    in_reply_to = msg.get("In-Reply-To")

    date_str = msg.get("Date", "")
    msg_date = datetime.utcnow()
    try:
        msg_date_tuple = email.utils.parsedate_tz(date_str)
        if msg_date_tuple:
            msg_date = datetime.fromtimestamp(email.utils.mktime_tz(msg_date_tuple))
    except Exception:
        pass

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                payload = part.get_payload(decode=True)
                if payload is not None:
                    body = payload.decode(errors="replace")
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload is not None:
            body = payload.decode(errors="replace")

    return {
        "subject": subject,
        "sender": sender,
        "recipient": recipient,
        "message_id": message_id,
        "in_reply_to": in_reply_to,
        "date": msg_date,
        "body": body
    }



def fetch_new_emails(mail, db: Session):
    status, messages = mail.search(None, "UNSEEN")
    if status != "OK":
        print("No new emails found.")
        return

    email_ids = messages[0].split()
    if not email_ids:
        print("No new emails found.")
        return

    for num in email_ids:
        status, data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            continue

        for response_part in data:
            if isinstance(response_part, tuple):
                raw_email = response_part[1]
                email_data = parse_email_message(raw_email)
                handle_incoming_email(db, email_data)


def handle_incoming_email(db: Session, email_data: dict):
    if email_data["in_reply_to"]:
        original_email = db.query(Email).filter(Email.message_id == email_data["in_reply_to"]).first()
        if original_email:
            original_email.status = "Replied"
            db.commit()
            new_email = Email(
                sender=email_data["sender"] or "unknown",
                recipient=email_data["recipient"] or "unknown",
                subject=email_data["subject"] or "",
                body=email_data["body"] or "",
                sent_timestamp=email_data["date"],
                message_id=email_data["message_id"] or "",
                in_reply_to=email_data["in_reply_to"],
                status="Pending",
                reply_timestamp=datetime.utcnow(),
            )
            db.add(new_email)
            db.commit()
            db.refresh(new_email)
            print(f"Reply processed: {new_email.subject}")
        else:
            save_new_email(db, email_data, status="Received")
    else:
        save_new_email(db, email_data, status="Received")

def save_new_email(db: Session, email_data: dict, status: str = "Received"):
    new_email = Email(
        sender=email_data["sender"] or "unknown",
        recipient=email_data["recipient"] or "unknown",
        subject=email_data["subject"] or "",
        body=email_data["body"] or "",
        sent_timestamp=email_data["date"],
        message_id=email_data["message_id"] or "",
        status=status,
    )
    db.add(new_email)
    db.commit()
    db.refresh(new_email)
    print(f"New email saved: {new_email.subject}")

def sync_emails():
    mail = connect_to_imap()
    try:
        db_session = next(get_db())
        fetch_new_emails(mail, db_session)
    except Exception as e:
        print(f"IMAP fetch error: {e}")
    finally:
        mail.logout()

@router.get("/sync-emails", dependencies=[Depends(get_current_active_superuser)])
def sync_emails_background(background_tasks: BackgroundTasks):
    """
    Endpoint to trigger background synchronization of emails via IMAP.
    """
    background_tasks.add_task(sync_emails)
    return {"message": "Syncing emails in the background."}
