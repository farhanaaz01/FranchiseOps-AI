from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    DashboardSummaryDTO,
    FranchiseComparisonDTO,
    OutletPerformanceDTO,
    UnderperformingOutletDTO,
)
from app.services import performance_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/outlets/{outlet_id}", response_model=OutletPerformanceDTO)
def get_outlet_performance(
    outlet_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        return performance_service.get_outlet_performance(db, outlet_id, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/franchises/{franchise_id}/compare", response_model=list[FranchiseComparisonDTO])
def compare_franchise_outlets(
    franchise_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    return performance_service.compare_outlets_in_franchise(db, franchise_id, start_date, end_date)


@router.get("/summary", response_model=DashboardSummaryDTO)
def get_dashboard_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    return performance_service.get_dashboard_summary(db, start_date, end_date)


@router.get("/underperforming", response_model=list[UnderperformingOutletDTO])
def get_underperforming_outlets(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    return performance_service.get_underperforming_outlets(db, start_date, end_date)
