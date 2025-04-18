# schemas/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ---------------------------
# Company Schemas
# ---------------------------
class CompanyBase(BaseModel):
    company_name: str
    domain: str



class CompanyOut(CompanyBase):
    company_id: int
    class Config:
        orm_mode = True

# ---------------------------
# Email Schemas
# ---------------------------
class EmailBase(BaseModel):
    sender: EmailStr
    recipient: EmailStr
    subject: str
    body: Optional[str] = None

class EmailCreate(EmailBase):
    pass
class EmailOut2(EmailBase):
    email_id: int
    sent_timestamp: datetime
    status: str
    domain: Optional[str] = None
    company_id: Optional[int] = None
    # Make message_id optional to allow None
    message_id: Optional[str] = None

    class Config:
        orm_mode = True
class EmailOut(EmailBase):
    email_id: int
    sent_timestamp: datetime
    status: str
    domain: Optional[str]
    company_id: Optional[int]
    message_id: str  # Ensure this field is present


    class Config:
        orm_mode = True

# ────────────────────────────────────────────────────────────────────
# 🔸  NEW – very small schema used by   /email-tracking/companies
# ────────────────────────────────────────────────────────────────────
class CompanyMinimal(BaseModel):
    company_id: int
    company_name: str

    class Config:                         # Pydantic v1
        orm_mode = True                   # (use `from_attributes=True` if v2)

class EmailOut1(BaseModel):
    email_id: int
    sender: str
    recipient: str
    subject: str
    body: str
    sent_timestamp: datetime
    status: str
    message_id: Optional[str] = None

    class Config:
        orm_mode = True

# ---------------------------
# User Schemas
# ---------------------------
class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

    class Config:
        orm_mode = True

# ---------------------------
# Auth Schemas
# ---------------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


# schemas/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CompanyOut(BaseModel):
    company_id: int
    company_name: str
    domain: str
    eligibility_criteria: str
    selection_process: str
    package_offered: str
    recruitment_year: int
    role_offered: str
    joining_date: Optional[datetime] = None
    job_type: str
    location: Optional[str] = None
    work_environment: Optional[str] = None
    recruitment_mode: Optional[str] = None

    class Config:
        # For Pydantic v1, use orm_mode = True.
        # For Pydantic v2, use from_attributes = True.
        from_attributes = True


# schemas/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CompanyOut(BaseModel):
    company_id: int
    company_name: str
    domain: str
    eligibility_criteria: str
    selection_process: str
    package_offered: str
    recruitment_year: int
    role_offered: str
    joining_date: Optional[datetime]
    job_type: str
    location: Optional[str]
    work_environment: Optional[str]
    recruitment_mode: Optional[str]

    class Config:
        # For Pydantic V1 use orm_mode=True; for V2 use from_attributes=True:
        from_attributes = True

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# … your other schemas above …

class UpcomingRecruitmentOut(BaseModel):
    company_id: int
    company_name: str
    domain: Optional[str]
    eligibility_criteria: Optional[str]
    selection_process: Optional[str]
    package_offered: Optional[str]
    recruitment_year: int
    role_offered: Optional[str]
    joining_date: Optional[datetime]
    job_type: Optional[str]
    location: Optional[str]
    work_environment: Optional[str]
    recruitment_mode: Optional[str]
    event_id: int
    event_date: datetime

    class Config:
        orm_mode = True

class CompanyCreate(BaseModel):
    company_name: str
    domain: str = None
    eligibility_criteria: str = None
    selection_process: str = None
    package_offered: str = None
    recruitment_year: int = None
    role_offered: str = None
    joining_date: Optional[datetime] = None
    job_type: str = None
    location: Optional[str] = None
    work_environment: Optional[str] = None
    recruitment_mode: Optional[str] = None

# schemas/schemas.py  ▼ keep this single, canonical definition
class RecruitmentEventOut(BaseModel):
    event_id: int
    company_id: int
    event_date: datetime

    class Config:
        orm_mode = True

class RecruitmentEventCreate(BaseModel):
    company_id: int
    event_date: datetime


# schemas/schemas.py (append below your existing schemas)
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PlacementCreate(BaseModel):
    student_name: str
    student_roll: str
    company_id: int
    role_offered: str
    joining_date: Optional[datetime] = None
    package_offered: str
    placement_year: int

    class Config:
        orm_mode = True

class PlacementOut(BaseModel):
    placement_id: int
    student_name: Optional[str] = None
    student_roll: Optional[str] = None
    company_id: Optional[int] = None
    role_offered: Optional[str] = None
    joining_date: Optional[datetime] = None
    package_offered: Optional[str] = None
    placement_year: Optional[int] = None
    company_name: str  # Required field in the output

    class Config:
        orm_mode = True
