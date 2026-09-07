from sqlalchemy.orm import Session

from app.models import InventoryTransaction
from app.schemas import InventoryTransactionCreate
from app.services import inventory_service


def get_all(db: Session) -> list[InventoryTransaction]:
    return db.query(InventoryTransaction).all()


def get_by_id(db: Session, transaction_id: int) -> InventoryTransaction:
    transaction = db.query(InventoryTransaction).filter(InventoryTransaction.transaction_id == transaction_id).first()
    if not transaction:
        raise ValueError(f"Inventory transaction not found with id: {transaction_id}")
    return transaction


def get_by_inventory(db: Session, inventory_id: int) -> list[InventoryTransaction]:
    return db.query(InventoryTransaction).filter(InventoryTransaction.inventory_id == inventory_id).all()


def create(db: Session, transaction: InventoryTransactionCreate) -> InventoryTransaction:
    inventory = inventory_service.get_by_id(db, transaction.inventory_id)

    db_transaction = InventoryTransaction(
        inventory_id=transaction.inventory_id,
        transaction_date=transaction.transaction_date,
        transaction_type=transaction.transaction_type.upper(),
        quantity=transaction.quantity,
        reason=transaction.reason,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    # Also update current stock
    inventory_service.adjust_stock(
        db,
        transaction.inventory_id,
        transaction.quantity,
        transaction.transaction_type.upper(),
    )

    return db_transaction


def delete(db: Session, transaction_id: int) -> None:
    transaction = get_by_id(db, transaction_id)
    db.delete(transaction)
    db.commit()
