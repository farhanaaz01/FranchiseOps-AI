from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ExecutiveDashboardDTO
from app.services import executive_dashboard_service

router = APIRouter(prefix="/api/executive", tags=["Executive Dashboard"])


@router.get("/summary", response_model=ExecutiveDashboardDTO)
def get_executive_summary(db: Session = Depends(get_db)):
    return executive_dashboard_service.get_executive_dashboard(db)
