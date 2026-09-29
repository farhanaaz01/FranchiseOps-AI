from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models import AuditComplianceRecord, AuditInspection, Outlet
from app.schemas import AuditComplianceRecordCreate, AuditInspectionCreate


def _outlet_name(db: Session, outlet_id: int) -> str | None:
    outlet = db.query(Outlet).filter(Outlet.outlet_id == outlet_id).first()
    return outlet.outlet_name if outlet else None


def _attach_outlet_name(record, outlet_name: str | None):
    data = {
        c.name: getattr(record, c.name)
        for c in record.__table__.columns
    }
    data["outlet_name"] = outlet_name
    return data


# ---- Inspections ----


def list_inspections(db: Session) -> list[dict]:
    rows = db.query(AuditInspection).order_by(AuditInspection.inspection_date.desc()).all()
    return [_attach_outlet_name(r, _outlet_name(db, r.outlet_id)) for r in rows]


def get_inspection(db: Session, audit_id: int) -> dict:
    row = db.query(AuditInspection).filter(AuditInspection.audit_id == audit_id).first()
    if not row:
        raise ValueError(f"Audit inspection {audit_id} not found")
    return _attach_outlet_name(row, _outlet_name(db, row.outlet_id))


def create_inspection(db: Session, payload: AuditInspectionCreate) -> dict:
    if not db.query(Outlet).filter(Outlet.outlet_id == payload.outlet_id).first():
        raise ValueError(f"Outlet {payload.outlet_id} not found")
    row = AuditInspection(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return _attach_outlet_name(row, _outlet_name(db, row.outlet_id))


def update_inspection(db: Session, audit_id: int, payload: AuditInspectionCreate) -> dict:
    row = db.query(AuditInspection).filter(AuditInspection.audit_id == audit_id).first()
    if not row:
        raise ValueError(f"Audit inspection {audit_id} not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return _attach_outlet_name(row, _outlet_name(db, row.outlet_id))


def delete_inspection(db: Session, audit_id: int) -> None:
    row = db.query(AuditInspection).filter(AuditInspection.audit_id == audit_id).first()
    if not row:
        raise ValueError(f"Audit inspection {audit_id} not found")
    db.delete(row)
    db.commit()


# ---- Compliance records ----


def list_compliance_records(db: Session, outlet_id: int | None = None) -> list[dict]:
    q = db.query(AuditComplianceRecord).order_by(AuditComplianceRecord.record_date.desc())
    if outlet_id is not None:
        q = q.filter(AuditComplianceRecord.outlet_id == outlet_id)
    rows = q.all()
    return [_attach_outlet_name(r, _outlet_name(db, r.outlet_id)) for r in rows]


def create_compliance_record(db: Session, payload: AuditComplianceRecordCreate) -> dict:
    if not db.query(Outlet).filter(Outlet.outlet_id == payload.outlet_id).first():
        raise ValueError(f"Outlet {payload.outlet_id} not found")
    row = AuditComplianceRecord(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return _attach_outlet_name(row, _outlet_name(db, row.outlet_id))


def average_compliance(db: Session) -> Decimal:
    from sqlalchemy import func

    avg = db.query(func.avg(AuditComplianceRecord.compliance_score)).scalar()
    if avg is None:
        return Decimal("0.00")
    return Decimal(str(avg)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
