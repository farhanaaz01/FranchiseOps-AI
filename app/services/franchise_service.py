from sqlalchemy.orm import Session

from app.models import Franchise
from app.schemas import FranchiseCreate, FranchiseResponse


def get_all(db: Session) -> list[Franchise]:
    return db.query(Franchise).all()


def get_by_id(db: Session, franchise_id: int) -> Franchise:
    franchise = db.query(Franchise).filter(Franchise.franchise_id == franchise_id).first()
    if not franchise:
        raise ValueError(f"Franchise not found with id: {franchise_id}")
    return franchise


def create(db: Session, franchise: FranchiseCreate) -> Franchise:
    db_franchise = Franchise(**franchise.model_dump())
    db.add(db_franchise)
    db.commit()
    db.refresh(db_franchise)
    return db_franchise


def update(db: Session, franchise_id: int, franchise_update: FranchiseCreate) -> Franchise:
    franchise = get_by_id(db, franchise_id)
    for key, value in franchise_update.model_dump().items():
        setattr(franchise, key, value)
    db.commit()
    db.refresh(franchise)
    return franchise


def delete(db: Session, franchise_id: int) -> None:
    franchise = get_by_id(db, franchise_id)
    db.delete(franchise)
    db.commit()
