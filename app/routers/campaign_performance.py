from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CampaignPerformanceCreate, CampaignPerformanceResponse
from app.services import campaign_performance_service

router = APIRouter(prefix="/api/campaign-performances", tags=["Campaign Performances"])


@router.get("", response_model=list[CampaignPerformanceResponse])
def get_all_performances(db: Session = Depends(get_db)):
    return campaign_performance_service.get_all(db)


@router.get("/{performance_id}", response_model=CampaignPerformanceResponse)
def get_performance(performance_id: int, db: Session = Depends(get_db)):
    try:
        return campaign_performance_service.get_by_id(db, performance_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/campaign/{campaign_id}", response_model=list[CampaignPerformanceResponse])
def get_performances_by_campaign(campaign_id: int, db: Session = Depends(get_db)):
    try:
        return campaign_performance_service.get_by_campaign(db, campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=CampaignPerformanceResponse, status_code=status.HTTP_201_CREATED)
def create_performance(performance: CampaignPerformanceCreate, db: Session = Depends(get_db)):
    try:
        return campaign_performance_service.create(db, performance)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{performance_id}", response_model=CampaignPerformanceResponse)
def update_performance(performance_id: int, performance: CampaignPerformanceCreate, db: Session = Depends(get_db)):
    try:
        return campaign_performance_service.update(db, performance_id, performance)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{performance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_performance(performance_id: int, db: Session = Depends(get_db)):
    try:
        campaign_performance_service.delete(db, performance_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
