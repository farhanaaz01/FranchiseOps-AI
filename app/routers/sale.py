from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SaleCreate, SaleResponse
from app.services import sale_service

router = APIRouter(prefix="/api/sales", tags=["Sales"])


@router.get("", response_model=list[SaleResponse])
def get_all_sales(db: Session = Depends(get_db)):
    return sale_service.get_all(db)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    try:
        return sale_service.get_by_id(db, sale_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/outlet/{outlet_id}", response_model=list[SaleResponse])
def get_sales_by_outlet(outlet_id: int, db: Session = Depends(get_db)):
    return sale_service.get_by_outlet(db, outlet_id)


@router.post("", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    try:
        return sale_service.create(db, sale)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(sale_id: int, sale: SaleCreate, db: Session = Depends(get_db)):
    try:
        return sale_service.update(db, sale_id, sale)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    try:
        sale_service.delete(db, sale_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
