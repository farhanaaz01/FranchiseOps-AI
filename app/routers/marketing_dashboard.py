from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CampaignAnalyticsDTO, MarketingDashboardDTO
from app.services import marketing_analytics_service

router = APIRouter(prefix="/api/marketing/dashboard", tags=["Marketing Dashboard"])


@router.get("/summary", response_model=MarketingDashboardDTO)
def get_marketing_summary(db: Session = Depends(get_db)):
    return marketing_analytics_service.get_marketing_dashboard(db)


@router.get("/campaigns/{campaign_id}", response_model=CampaignAnalyticsDTO)
def get_campaign_analytics(campaign_id: int, db: Session = Depends(get_db)):
    try:
        return marketing_analytics_service.analyze_campaign(db, campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/campaigns", response_model=list[CampaignAnalyticsDTO])
def get_all_campaign_analytics(db: Session = Depends(get_db)):
    return marketing_analytics_service.get_all_campaign_analytics(db)
