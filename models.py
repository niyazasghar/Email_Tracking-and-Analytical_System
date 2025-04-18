# models.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

# models.py (Add recruitment-related fields)

class Company(Base):
    __tablename__ = "companies"
    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    domain = Column(String(100), nullable=True)
    eligibility_criteria = Column(Text, nullable=True)
    selection_process = Column(Text, nullable=True)
    package_offered = Column(String(100), nullable=True)
    recruitment_year = Column(Integer, nullable=True)
    role_offered = Column(String(255), nullable=True)
    joining_date = Column(DateTime, nullable=True)
    job_type = Column(String(50), nullable=True)  # Full-Time, Internship, etc.
    location = Column(String(255), nullable=True)
    work_environment = Column(String(100), nullable=True)
    recruitment_mode = Column(String(50), nullable=True)  # Online/Offline recruitment

    recruitment_events = relationship("RecruitmentEvent", back_populates="company")


class RecruitmentEvent(Base):
    __tablename__ = "recruitment_events"
    event_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    event_date = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="recruitment_events")

class Email(Base):
    __tablename__ = "emails"
    email_id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(100), nullable=False)
    recipient = Column(String(100), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text)
    sent_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(50), default="Sent", nullable=False)
    domain = Column(String(100))
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)
    reply_timestamp= Column(DateTime, nullable=True)
    # For preventing duplicates and linking replies
    message_id = Column(String, unique=True, index=True, nullable=True)
    in_reply_to = Column(String, nullable=True)  # store parent's Message-ID

    company = relationship("Company", backref="emails")

# models.py (append below your existing models)
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship



class Placement(Base):
    __tablename__ = "placements"
    placement_id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String(100), nullable=True)
    student_roll = Column(String(50), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)
    role_offered = Column(String(255), nullable=True)
    joining_date = Column(DateTime, nullable=True)
    package_offered = Column(String(100), nullable=True)
    placement_year = Column(Integer, nullable=True)

    # Relationship to Company for fetching the company name
    company = relationship("Company", backref="placements")
