from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AuditDashboardDTO, ComplianceOutletSummaryDTO
from app.services import audit_analytics_service

router = APIRouter(prefix="/api/audit/dashboard", tags=["Audit Dashboard"])


@router.get("/summary", response_model=AuditDashboardDTO)
def get_audit_dashboard_summary(db: Session = Depends(get_db)):
    return audit_analytics_service.get_audit_dashboard(db)


@router.get("/compliance", response_model=list[ComplianceOutletSummaryDTO])
def get_compliance_by_outlet(db: Session = Depends(get_db)):
    return audit_analytics_service.get_compliance_summaries(db)
