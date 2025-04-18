# routers/analytics.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Dict, Optional, List, Union

from db import get_db
from models import Email, Company, Placement
from routers.auth import get_current_active_superuser

from schemas.analytics import (
    PlacementYearAllCompanies,
    PlacementYearSingleCompany, PlacementCompanyStat
)

router = APIRouter(prefix="/analytics", tags=["Analytics Dashboard"])


def get_time_filter(start_date: Optional[datetime], end_date: Optional[datetime]):
    filters = []
    if start_date:
        filters.append(Email.sent_timestamp >= start_date)
    if end_date:
        filters.append(Email.sent_timestamp <= end_date)
    return filters


@router.get("/companies")
def get_companies(db: Session = Depends(get_db)) -> List[Dict[str, Union[int, str]]]:
    companies = db.query(Company.company_id, Company.company_name).all()
    result = [{"id": 0, "name": "All Companies"}]
    for c_id, c_name in companies:
        result.append({"id": c_id, "name": c_name})
    return result


@router.get("/overview", dependencies=[Depends(get_current_active_superuser)])
def analytics_overview(
    company_id: int = Query(0, description="0 means all companies"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
) -> Dict[str, Union[Dict, List[Dict[str, Union[int, str, float]]]]]:
    time_filters = get_time_filter(start_date, end_date)
    if company_id:
        time_filters.append(Email.company_id == company_id)

    total_emails = db.query(Email).filter(*time_filters).count()
    replied_emails = db.query(Email).filter(*time_filters, Email.status == "Replied").count()
    avg_response = 0.0  # placeholder

    status_dist = dict(
        db.query(Email.status, func.count(Email.email_id))
          .filter(*time_filters)
          .group_by(Email.status)
          .all()
    )

    conversion_rate = round((replied_emails / total_emails) * 100, 2) if total_emails else 0

    # company‐level breakdown
    company_stats: List[Dict[str, Union[int, str, float]]] = []
    target_companies = (
        [db.query(Company).get(company_id)]
        if company_id
        else db.query(Company).all()
    )
    for comp in target_companies:
        if not comp:
            continue
        sent_count = db.query(Email).filter(*time_filters, Email.company_id == comp.company_id).count()
        replied_count = db.query(Email).filter(
            *time_filters, Email.company_id == comp.company_id, Email.status == "Replied"
        ).count()
        comp_conv = round((replied_count / sent_count) * 100, 2) if sent_count else 0
        company_stats.append({
            "company_id": comp.company_id,
            "company_name": comp.company_name,
            "sent": sent_count,
            "replied": replied_count,
            "conversion_rate": comp_conv
        })

    # hourly reply distribution
    hourly_data = db.query(
        func.extract('hour', Email.sent_timestamp).label('hour'),
        func.count(Email.email_id).label('count')
    ).filter(*time_filters, Email.status == "Replied") \
     .group_by('hour') \
     .order_by('hour') \
     .all()

    hours = [f"{i:02d}:00" for i in range(24)]
    reply_counts = [0]*24
    for hour, cnt in hourly_data:
        reply_counts[int(hour)] = cnt

    return {
        "overall": {
            "total_emails": total_emails,
            "replied_emails": replied_emails,
            "pending_emails": total_emails - replied_emails,
            "avg_response_time": round(avg_response, 2),
            "status_distribution": status_dist,
            "conversion_rate": conversion_rate
        },
        "companies": company_stats,
        "charts": {
            "hourly_distribution": {"labels": hours, "data": reply_counts},
            "status_distribution": {
                "labels": list(status_dist.keys()),
                "data": list(status_dist.values())
            }
        }
    }


@router.get(
    "/placements",
    response_model=Union[PlacementYearAllCompanies, PlacementYearSingleCompany],
    dependencies=[Depends(get_current_active_superuser)]
)
def get_placement_analytics(
    year: int = Query(..., description="e.g. 2025"),
    company_id: int = Query(0, description="0 = all"),
    db: Session = Depends(get_db)
):
    if company_id:
        count = db.query(func.count(Placement.placement_id)).filter(
            Placement.placement_year == year,
            Placement.company_id == company_id
        ).scalar()
        comp = db.query(Company).get(company_id)
        return PlacementYearSingleCompany(
            year=year,
            company_id=company_id,
            company_name=comp.company_name if comp else "Unknown",
            placements_count=count or 0
        )

    results = db.query(
        Placement.company_id,
        func.count(Placement.placement_id).label("placements_count")
    ).filter(Placement.placement_year == year) \
     .group_by(Placement.company_id) \
     .all()

    summary = [
        PlacementCompanyStat(
            company_id=comp_id,
            company_name=(db.query(Company).get(comp_id) or Company(company_id=comp_id, company_name="Unknown")).company_name,
            placements_count=count
        )
        for comp_id, count in results
    ]
    return PlacementYearAllCompanies(year=year, placements=summary)
