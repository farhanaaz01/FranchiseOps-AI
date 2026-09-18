from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MarketingCampaignCreate, MarketingCampaignResponse
from app.services import marketing_campaign_service

router = APIRouter(prefix="/api/marketing-campaigns", tags=["Marketing Campaigns"])


@router.get("", response_model=list[MarketingCampaignResponse])
def get_all_campaigns(db: Session = Depends(get_db)):
    return marketing_campaign_service.get_all(db)


@router.get("/{campaign_id}", response_model=MarketingCampaignResponse)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    try:
        return marketing_campaign_service.get_by_id(db, campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/outlet/{outlet_id}", response_model=list[MarketingCampaignResponse])
def get_campaigns_by_outlet(outlet_id: int, db: Session = Depends(get_db)):
    return marketing_campaign_service.get_by_outlet(db, outlet_id)


@router.post("", response_model=MarketingCampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign: MarketingCampaignCreate, db: Session = Depends(get_db)):
    try:
        return marketing_campaign_service.create(db, campaign)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{campaign_id}", response_model=MarketingCampaignResponse)
def update_campaign(campaign_id: int, campaign: MarketingCampaignCreate, db: Session = Depends(get_db)):
    try:
        return marketing_campaign_service.update(db, campaign_id, campaign)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    try:
        marketing_campaign_service.delete(db, campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
