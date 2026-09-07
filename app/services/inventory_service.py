from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Inventory
from app.schemas import InventoryCreate, InventoryUpdate
from app.services import outlet_service, product_service


def get_all(db: Session) -> list[Inventory]:
    return db.query(Inventory).all()


def get_by_id(db: Session, inventory_id: int) -> Inventory:
    inventory = db.query(Inventory).filter(Inventory.inventory_id == inventory_id).first()
    if not inventory:
        raise ValueError(f"Inventory not found with id: {inventory_id}")
    return inventory


def get_by_outlet(db: Session, outlet_id: int) -> list[Inventory]:
    return db.query(Inventory).filter(Inventory.outlet_id == outlet_id).all()


def get_by_outlet_and_product(db: Session, outlet_id: int, product_id: int) -> Optional[Inventory]:
    return (
        db.query(Inventory)
        .filter(Inventory.outlet_id == outlet_id, Inventory.product_id == product_id)
        .first()
    )


def create(db: Session, inventory: InventoryCreate) -> Inventory:
    outlet_service.get_by_id(db, inventory.outlet_id)
    product_service.get_by_id(db, inventory.product_id)

    db_inventory = Inventory(
        outlet_id=inventory.outlet_id,
        product_id=inventory.product_id,
        current_stock=inventory.current_stock or Decimal("0.00"),
        reorder_point=inventory.reorder_point or Decimal("0.00"),
        reorder_quantity=inventory.reorder_quantity or Decimal("0.00"),
        max_stock=inventory.max_stock,
        last_updated=inventory.last_updated or date.today(),
    )
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def update(db: Session, inventory_id: int, inventory_update: InventoryUpdate) -> Inventory:
    inventory = get_by_id(db, inventory_id)
    if inventory_update.current_stock is not None:
        inventory.current_stock = inventory_update.current_stock
    if inventory_update.reorder_point is not None:
        inventory.reorder_point = inventory_update.reorder_point
    if inventory_update.reorder_quantity is not None:
        inventory.reorder_quantity = inventory_update.reorder_quantity
    if inventory_update.max_stock is not None:
        inventory.max_stock = inventory_update.max_stock
    inventory.last_updated = inventory_update.last_updated or date.today()
    db.commit()
    db.refresh(inventory)
    return inventory


def delete(db: Session, inventory_id: int) -> None:
    inventory = get_by_id(db, inventory_id)
    db.delete(inventory)
    db.commit()


def adjust_stock(db: Session, inventory_id: int, quantity: Decimal, transaction_type: str) -> Inventory:
    inventory = get_by_id(db, inventory_id)
    if transaction_type == "IN":
        inventory.current_stock += quantity
    elif transaction_type in ("OUT", "WASTAGE"):
        inventory.current_stock -= quantity
    elif transaction_type == "RETURN":
        inventory.current_stock += quantity
    inventory.last_updated = date.today()
    db.commit()
    db.refresh(inventory)
    return inventory
