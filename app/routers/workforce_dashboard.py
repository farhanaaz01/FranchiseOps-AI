from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    EmployeePerformanceDTO,
    OutletWorkforceDTO,
    StaffingAlertDTO,
    WorkforceDashboardDTO,
)
from app.services import workforce_analytics_service

router = APIRouter(prefix="/api/workforce/dashboard", tags=["Workforce Dashboard"])


@router.get("/summary", response_model=WorkforceDashboardDTO)
def get_workforce_summary(db: Session = Depends(get_db)):
    return workforce_analytics_service.get_workforce_dashboard(db)


@router.get("/outlets/{outlet_id}", response_model=OutletWorkforceDTO)
def get_outlet_workforce(
    outlet_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        return workforce_analytics_service.analyze_outlet_workforce(db, outlet_id, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/employees/{employee_id}", response_model=EmployeePerformanceDTO)
def get_employee_performance(
    employee_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        return workforce_analytics_service.analyze_employee(db, employee_id, start_date, end_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/alerts", response_model=list[StaffingAlertDTO])
def get_staffing_alerts(db: Session = Depends(get_db)):
    return workforce_analytics_service.get_all_staffing_alerts(db)
