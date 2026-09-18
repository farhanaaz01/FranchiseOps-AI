from sqlalchemy.orm import Session

from app.models import Attendance
from app.schemas import AttendanceCreate, AttendanceResponse
from app.services import employee_service


def get_all(db: Session) -> list[Attendance]:
    return db.query(Attendance).all()


def get_by_id(db: Session, attendance_id: int) -> Attendance:
    attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    if not attendance:
        raise ValueError(f"Attendance record not found with id: {attendance_id}")
    return attendance


def get_by_employee(db: Session, employee_id: int) -> list[Attendance]:
    employee_service.get_by_id(db, employee_id)
    return db.query(Attendance).filter(Attendance.employee_id == employee_id).all()


def create(db: Session, attendance: AttendanceCreate) -> Attendance:
    employee_service.get_by_id(db, attendance.employee_id)
    db_attendance = Attendance(**attendance.model_dump())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


def update(db: Session, attendance_id: int, attendance_update: AttendanceCreate) -> Attendance:
    attendance = get_by_id(db, attendance_id)
    attendance.employee_id = attendance_update.employee_id
    attendance.attendance_date = attendance_update.attendance_date
    attendance.status = attendance_update.status
    attendance.hours_worked = attendance_update.hours_worked
    attendance.notes = attendance_update.notes
    db.commit()
    db.refresh(attendance)
    return attendance


def delete(db: Session, attendance_id: int) -> None:
    attendance = get_by_id(db, attendance_id)
    db.delete(attendance)
    db.commit()
