from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import InventoryTransactionCreate, InventoryTransactionResponse
from app.services import inventory_transaction_service

router = APIRouter(prefix="/api/inventory-transactions", tags=["Inventory Transactions"])


@router.get("", response_model=list[InventoryTransactionResponse])
def get_all_transactions(db: Session = Depends(get_db)):
    return inventory_transaction_service.get_all(db)


@router.get("/{transaction_id}", response_model=InventoryTransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    try:
        return inventory_transaction_service.get_by_id(db, transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/inventory/{inventory_id}", response_model=list[InventoryTransactionResponse])
def get_transactions_by_inventory(inventory_id: int, db: Session = Depends(get_db)):
    return inventory_transaction_service.get_by_inventory(db, inventory_id)


@router.post("", response_model=InventoryTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: InventoryTransactionCreate, db: Session = Depends(get_db)):
    try:
        return inventory_transaction_service.create(db, transaction)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    try:
        inventory_transaction_service.delete(db, transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
