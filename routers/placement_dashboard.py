from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import get_db
from models import Placement, Company
from schemas.schemas import PlacementOut
from typing import List, Optional
from routers.auth import get_current_active_superuser, User

router = APIRouter(prefix="/placement", tags=["Placement Dashboard"])

@router.get("/students", response_model=List[PlacementOut], dependencies=[Depends(get_current_active_superuser)])
def get_placed_students(
    company_id: int = Query(0, description="Company ID for filtering. Use 0 for all companies.", example=0),
    year: Optional[int] = Query(None, description="Placement year (e.g., 2025)", example=2025),
    role: Optional[str] = Query(None, description="Role offered (e.g., 'Software Engineer')", example="Software Engineer"),
    db: Session = Depends(get_db)
) -> List[PlacementOut]:
    """
    Fetch placed students, superuser only.
    """
    query = db.query(Placement, Company.company_name).join(Company, Company.company_id == Placement.company_id)

    if company_id != 0:
        query = query.filter(Placement.company_id == company_id)
    if year is not None:
        query = query.filter(Placement.placement_year == year)
    if role:
        query = query.filter(Placement.role_offered.ilike(f"%{role}%"))

    results = query.all()
    placements = []
    for placement, comp_name in results:
        placement_dict = placement.__dict__.copy()
        placement_dict.pop("_sa_instance_state", None)
        placement_dict["company_name"] = comp_name
        placements.append(placement_dict)
    return placements
