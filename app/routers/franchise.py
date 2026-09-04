from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import FranchiseCreate, FranchiseResponse
from app.services import franchise_service

router = APIRouter(prefix="/api/franchises", tags=["Franchises"])


@router.get("", response_model=list[FranchiseResponse])
def get_all_franchises(db: Session = Depends(get_db)):
    return franchise_service.get_all(db)


@router.get("/{franchise_id}", response_model=FranchiseResponse)
def get_franchise(franchise_id: int, db: Session = Depends(get_db)):
    try:
        return franchise_service.get_by_id(db, franchise_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=FranchiseResponse, status_code=status.HTTP_201_CREATED)
def create_franchise(franchise: FranchiseCreate, db: Session = Depends(get_db)):
    return franchise_service.create(db, franchise)


@router.put("/{franchise_id}", response_model=FranchiseResponse)
def update_franchise(franchise_id: int, franchise: FranchiseCreate, db: Session = Depends(get_db)):
    try:
        return franchise_service.update(db, franchise_id, franchise)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{franchise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_franchise(franchise_id: int, db: Session = Depends(get_db)):
    try:
        franchise_service.delete(db, franchise_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
