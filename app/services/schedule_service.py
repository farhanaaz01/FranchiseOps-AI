from sqlalchemy.orm import Session

from app.models import Schedule
from app.schemas import ScheduleCreate, ScheduleResponse
from app.services import employee_service


def get_all(db: Session) -> list[Schedule]:
    return db.query(Schedule).all()


def get_by_id(db: Session, schedule_id: int) -> Schedule:
    schedule = db.query(Schedule).filter(Schedule.schedule_id == schedule_id).first()
    if not schedule:
        raise ValueError(f"Schedule not found with id: {schedule_id}")
    return schedule


def get_by_employee(db: Session, employee_id: int) -> list[Schedule]:
    employee_service.get_by_id(db, employee_id)
    return db.query(Schedule).filter(Schedule.employee_id == employee_id).all()


def create(db: Session, schedule: ScheduleCreate) -> Schedule:
    employee_service.get_by_id(db, schedule.employee_id)
    db_schedule = Schedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule


def update(db: Session, schedule_id: int, schedule_update: ScheduleCreate) -> Schedule:
    schedule = get_by_id(db, schedule_id)
    schedule.employee_id = schedule_update.employee_id
    schedule.schedule_date = schedule_update.schedule_date
    schedule.shift_start = schedule_update.shift_start
    schedule.shift_end = schedule_update.shift_end
    schedule.status = schedule_update.status
    db.commit()
    db.refresh(schedule)
    return schedule


def delete(db: Session, schedule_id: int) -> None:
    schedule = get_by_id(db, schedule_id)
    db.delete(schedule)
    db.commit()
