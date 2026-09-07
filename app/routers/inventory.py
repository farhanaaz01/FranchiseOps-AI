from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import InventoryCreate, InventoryResponse, InventoryUpdate
from app.services import inventory_service

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("", response_model=list[InventoryResponse])
def get_all_inventory(db: Session = Depends(get_db)):
    return inventory_service.get_all(db)


@router.get("/{inventory_id}", response_model=InventoryResponse)
def get_inventory(inventory_id: int, db: Session = Depends(get_db)):
    try:
        return inventory_service.get_by_id(db, inventory_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/outlet/{outlet_id}", response_model=list[InventoryResponse])
def get_inventory_by_outlet(outlet_id: int, db: Session = Depends(get_db)):
    return inventory_service.get_by_outlet(db, outlet_id)


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    try:
        return inventory_service.create(db, inventory)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{inventory_id}", response_model=InventoryResponse)
def update_inventory(inventory_id: int, inventory: InventoryUpdate, db: Session = Depends(get_db)):
    try:
        return inventory_service.update(db, inventory_id, inventory)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory(inventory_id: int, db: Session = Depends(get_db)):
    try:
        inventory_service.delete(db, inventory_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
