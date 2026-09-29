from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    AuditComplianceRecordCreate,
    AuditComplianceRecordResponse,
    AuditInspectionCreate,
    AuditInspectionResponse,
)
from app.services import audit_service

router = APIRouter(prefix="/api/audits", tags=["Audit"])


@router.get("/inspections", response_model=list[AuditInspectionResponse])
def list_inspections(db: Session = Depends(get_db)):
    return audit_service.list_inspections(db)


@router.get("/inspections/{audit_id}", response_model=AuditInspectionResponse)
def get_inspection(audit_id: int, db: Session = Depends(get_db)):
    try:
        return audit_service.get_inspection(db, audit_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/inspections", response_model=AuditInspectionResponse, status_code=status.HTTP_201_CREATED)
def create_inspection(payload: AuditInspectionCreate, db: Session = Depends(get_db)):
    try:
        return audit_service.create_inspection(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/inspections/{audit_id}", response_model=AuditInspectionResponse)
def update_inspection(audit_id: int, payload: AuditInspectionCreate, db: Session = Depends(get_db)):
    try:
        return audit_service.update_inspection(db, audit_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/inspections/{audit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inspection(audit_id: int, db: Session = Depends(get_db)):
    try:
        audit_service.delete_inspection(db, audit_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/compliance", response_model=list[AuditComplianceRecordResponse])
def list_compliance_records(outlet_id: int | None = None, db: Session = Depends(get_db)):
    return audit_service.list_compliance_records(db, outlet_id)


@router.post("/compliance", response_model=AuditComplianceRecordResponse, status_code=status.HTTP_201_CREATED)
def create_compliance_record(payload: AuditComplianceRecordCreate, db: Session = Depends(get_db)):
    try:
        return audit_service.create_compliance_record(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
