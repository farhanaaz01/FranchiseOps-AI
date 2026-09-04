from sqlalchemy.orm import Session

from app.models import Franchise, Outlet
from app.schemas import OutletCreate, OutletResponse
from app.services import franchise_service


def get_all(db: Session) -> list[Outlet]:
    return db.query(Outlet).all()


def get_by_id(db: Session, outlet_id: int) -> Outlet:
    outlet = db.query(Outlet).filter(Outlet.outlet_id == outlet_id).first()
    if not outlet:
        raise ValueError(f"Outlet not found with id: {outlet_id}")
    return outlet


def get_by_franchise(db: Session, franchise_id: int) -> list[Outlet]:
    return db.query(Outlet).filter(Outlet.franchise_id == franchise_id).all()


def create(db: Session, outlet: OutletCreate) -> Outlet:
    franchise = franchise_service.get_by_id(db, outlet.franchise_id)
    db_outlet = Outlet(
        franchise_id=outlet.franchise_id,
        outlet_name=outlet.outlet_name,
        location=outlet.location,
        status=outlet.status,
    )
    db.add(db_outlet)
    db.commit()
    db.refresh(db_outlet)
    return db_outlet


def update(db: Session, outlet_id: int, outlet_update: OutletCreate) -> Outlet:
    outlet = get_by_id(db, outlet_id)
    outlet.outlet_name = outlet_update.outlet_name
    outlet.location = outlet_update.location
    outlet.status = outlet_update.status
    db.commit()
    db.refresh(outlet)
    return outlet


def delete(db: Session, outlet_id: int) -> None:
    outlet = get_by_id(db, outlet_id)
    db.delete(outlet)
    db.commit()
