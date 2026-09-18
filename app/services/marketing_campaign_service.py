from sqlalchemy.orm import Session

from app.models import MarketingCampaign
from app.schemas import MarketingCampaignCreate, MarketingCampaignResponse
from app.services import outlet_service


def get_all(db: Session) -> list[MarketingCampaign]:
    return db.query(MarketingCampaign).all()


def get_by_id(db: Session, campaign_id: int) -> MarketingCampaign:
    campaign = db.query(MarketingCampaign).filter(MarketingCampaign.campaign_id == campaign_id).first()
    if not campaign:
        raise ValueError(f"Campaign not found with id: {campaign_id}")
    return campaign


def get_by_outlet(db: Session, outlet_id: int) -> list[MarketingCampaign]:
    return db.query(MarketingCampaign).filter(MarketingCampaign.outlet_id == outlet_id).all()


def create(db: Session, campaign: MarketingCampaignCreate) -> MarketingCampaign:
    outlet_service.get_by_id(db, campaign.outlet_id)
    db_campaign = MarketingCampaign(**campaign.model_dump())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def update(db: Session, campaign_id: int, campaign_update: MarketingCampaignCreate) -> MarketingCampaign:
    campaign = get_by_id(db, campaign_id)
    for key, value in campaign_update.model_dump().items():
        setattr(campaign, key, value)
    db.commit()
    db.refresh(campaign)
    return campaign


def delete(db: Session, campaign_id: int) -> None:
    campaign = get_by_id(db, campaign_id)
    db.delete(campaign)
    db.commit()
