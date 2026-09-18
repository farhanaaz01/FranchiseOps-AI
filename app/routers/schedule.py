from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ScheduleCreate, ScheduleResponse
from app.services import schedule_service

router = APIRouter(prefix="/api/schedules", tags=["Schedules"])


@router.get("", response_model=list[ScheduleResponse])
def get_all_schedules(db: Session = Depends(get_db)):
    return schedule_service.get_all(db)


@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    try:
        return schedule_service.get_by_id(db, schedule_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/employee/{employee_id}", response_model=list[ScheduleResponse])
def get_schedules_by_employee(employee_id: int, db: Session = Depends(get_db)):
    try:
        return schedule_service.get_by_employee(db, employee_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    try:
        return schedule_service.create(db, schedule)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(schedule_id: int, schedule: ScheduleCreate, db: Session = Depends(get_db)):
    try:
        return schedule_service.update(db, schedule_id, schedule)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    try:
        schedule_service.delete(db, schedule_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
