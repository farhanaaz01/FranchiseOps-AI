from sqlalchemy.orm import Session

from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeResponse
from app.services import outlet_service


def get_all(db: Session) -> list[Employee]:
    return db.query(Employee).all()


def get_by_id(db: Session, employee_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise ValueError(f"Employee not found with id: {employee_id}")
    return employee


def get_by_outlet(db: Session, outlet_id: int) -> list[Employee]:
    return db.query(Employee).filter(Employee.outlet_id == outlet_id).all()


def create(db: Session, employee: EmployeeCreate) -> Employee:
    outlet_service.get_by_id(db, employee.outlet_id)
    db_employee = Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def update(db: Session, employee_id: int, employee_update: EmployeeCreate) -> Employee:
    employee = get_by_id(db, employee_id)
    for key, value in employee_update.model_dump().items():
        setattr(employee, key, value)
    db.commit()
    db.refresh(employee)
    return employee


def delete(db: Session, employee_id: int) -> None:
    employee = get_by_id(db, employee_id)
    db.delete(employee)
    db.commit()
