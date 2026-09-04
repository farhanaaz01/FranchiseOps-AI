from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import OutletCreate, OutletResponse
from app.services import outlet_service

router = APIRouter(prefix="/api/outlets", tags=["Outlets"])


@router.get("", response_model=list[OutletResponse])
def get_all_outlets(db: Session = Depends(get_db)):
    return outlet_service.get_all(db)


@router.get("/{outlet_id}", response_model=OutletResponse)
def get_outlet(outlet_id: int, db: Session = Depends(get_db)):
    try:
        return outlet_service.get_by_id(db, outlet_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/franchise/{franchise_id}", response_model=list[OutletResponse])
def get_outlets_by_franchise(franchise_id: int, db: Session = Depends(get_db)):
    return outlet_service.get_by_franchise(db, franchise_id)


@router.post("", response_model=OutletResponse, status_code=status.HTTP_201_CREATED)
def create_outlet(outlet: OutletCreate, db: Session = Depends(get_db)):
    try:
        return outlet_service.create(db, outlet)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{outlet_id}", response_model=OutletResponse)
def update_outlet(outlet_id: int, outlet: OutletCreate, db: Session = Depends(get_db)):
    try:
        return outlet_service.update(db, outlet_id, outlet)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{outlet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outlet(outlet_id: int, db: Session = Depends(get_db)):
    try:
        outlet_service.delete(db, outlet_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
