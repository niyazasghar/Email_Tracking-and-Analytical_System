# schemas/analytics.py
from pydantic import BaseModel
from typing import List, Optional

class PlacementCompanyStat(BaseModel):
    company_id: int
    company_name: str
    placements_count: int

class PlacementYearAllCompanies(BaseModel):
    year: int
    placements: List[PlacementCompanyStat]

class PlacementYearSingleCompany(BaseModel):
    year: int
    company_id: int
    company_name: str
    placements_count: int
