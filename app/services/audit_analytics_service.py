from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import AuditComplianceRecord, AuditInspection, Outlet
from app.schemas import AuditDashboardDTO, AuditInspectionResponse, AuditComplianceRecordResponse, ComplianceOutletSummaryDTO
from app.services import audit_service, intelligence_service
from app.utils.outlet_id import format_pipeline_outlet_id


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


COMPLIANCE_THRESHOLD = Decimal("75.00")


def get_audit_dashboard(db: Session) -> AuditDashboardDTO:
    inspections = db.query(AuditInspection).all()
    total = len(inspections)
    if total:
        avg_score = _to_decimal(db.query(func.avg(AuditInspection.score)).scalar())
        passed = sum(1 for i in inspections if i.status == "Passed")
        warning = sum(1 for i in inspections if i.status == "Warning")
        failed = sum(1 for i in inspections if i.status == "Failed")
    else:
        avg_score = Decimal("0.00")
        passed = warning = failed = 0

    avg_compliance = audit_service.average_compliance(db)
    below_threshold = (
        db.query(func.count(func.distinct(AuditComplianceRecord.outlet_id)))
        .filter(AuditComplianceRecord.compliance_score < COMPLIANCE_THRESHOLD)
        .scalar()
        or 0
    )

    recent_raw = audit_service.list_inspections(db)[:10]
    recent = [AuditInspectionResponse.model_validate(r) for r in recent_raw]

    compliance_raw = audit_service.list_compliance_records(db)
    compliance_by_outlet = [AuditComplianceRecordResponse.model_validate(r) for r in compliance_raw[:20]]

    return AuditDashboardDTO(
        total_inspections=total,
        average_inspection_score=avg_score,
        passed_count=passed,
        warning_count=warning,
        failed_count=failed,
        average_compliance_score=avg_compliance,
        outlets_below_compliance_threshold=int(below_threshold),
        compliance_threshold=COMPLIANCE_THRESHOLD,
        recent_inspections=recent,
        compliance_by_outlet=compliance_by_outlet,
    )


def get_compliance_summaries(db: Session) -> list[ComplianceOutletSummaryDTO]:
    outlets = db.query(Outlet).all()
    pipeline = intelligence_service.get_latest(db)
    perf_map = {p.outlet_id: p for p in pipeline.performance_scores}
    kpi_map = {k.outlet_id: k for k in pipeline.kpis}

    summaries: list[ComplianceOutletSummaryDTO] = []
    for outlet in outlets:
        pid = format_pipeline_outlet_id(outlet.outlet_id)
        latest_record = (
            db.query(AuditComplianceRecord)
            .filter(AuditComplianceRecord.outlet_id == outlet.outlet_id)
            .order_by(AuditComplianceRecord.record_date.desc())
            .first()
        )
        latest_inspection = (
            db.query(AuditInspection)
            .filter(AuditInspection.outlet_id == outlet.outlet_id)
            .order_by(AuditInspection.inspection_date.desc())
            .first()
        )
        kpi = kpi_map.get(pid)
        perf = perf_map.get(pid)
        compliance = _to_decimal(latest_record.compliance_score if latest_record else (kpi.compliance_score if kpi else 0))
        summaries.append(
            ComplianceOutletSummaryDTO(
                outlet_id=outlet.outlet_id,
                pipeline_outlet_id=pid,
                outlet_name=outlet.outlet_name,
                compliance_score=compliance,
                violation_count=int(latest_record.violation_count if latest_record else 0),
                latest_inspection_score=_to_decimal(latest_inspection.score) if latest_inspection else None,
                inspection_status=latest_inspection.status if latest_inspection else None,
                health_status=perf.health_status if perf else None,
                performance_score=_to_decimal(perf.performance_score) if perf else None,
            )
        )
    summaries.sort(key=lambda s: s.compliance_score)
    return summaries
