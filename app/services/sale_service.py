from sqlalchemy.orm import Session

from app.models import Sale
from app.schemas import SaleCreate, SaleResponse
from app.services import outlet_service


def get_all(db: Session) -> list[Sale]:
    return db.query(Sale).all()


def get_by_id(db: Session, sale_id: int) -> Sale:
    sale = db.query(Sale).filter(Sale.sale_id == sale_id).first()
    if not sale:
        raise ValueError(f"Sale not found with id: {sale_id}")
    return sale


def get_by_outlet(db: Session, outlet_id: int) -> list[Sale]:
    return db.query(Sale).filter(Sale.outlet_id == outlet_id).all()


def create(db: Session, sale: SaleCreate) -> Sale:
    outlet_service.get_by_id(db, sale.outlet_id)
    db_sale = Sale(
        outlet_id=sale.outlet_id,
        sale_date=sale.sale_date,
        revenue=sale.revenue,
        transaction_count=sale.transaction_count,
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale


def update(db: Session, sale_id: int, sale_update: SaleCreate) -> Sale:
    sale = get_by_id(db, sale_id)
    sale.sale_date = sale_update.sale_date
    sale.revenue = sale_update.revenue
    sale.transaction_count = sale_update.transaction_count
    db.commit()
    db.refresh(sale)
    return sale


def delete(db: Session, sale_id: int) -> None:
    sale = get_by_id(db, sale_id)
    db.delete(sale)
    db.commit()
