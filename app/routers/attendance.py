from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AttendanceCreate, AttendanceResponse
from app.services import attendance_service

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.get("", response_model=list[AttendanceResponse])
def get_all_attendance(db: Session = Depends(get_db)):
    return attendance_service.get_all(db)


@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    try:
        return attendance_service.get_by_id(db, attendance_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/employee/{employee_id}", response_model=list[AttendanceResponse])
def get_attendance_by_employee(employee_id: int, db: Session = Depends(get_db)):
    try:
        return attendance_service.get_by_employee(db, employee_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    try:
        return attendance_service.create(db, attendance)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(attendance_id: int, attendance: AttendanceCreate, db: Session = Depends(get_db)):
    try:
        return attendance_service.update(db, attendance_id, attendance)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    try:
        attendance_service.delete(db, attendance_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
