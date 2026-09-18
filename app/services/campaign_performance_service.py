from sqlalchemy.orm import Session

from app.models import CampaignPerformance
from app.schemas import CampaignPerformanceCreate, CampaignPerformanceResponse
from app.services import marketing_campaign_service


def get_all(db: Session) -> list[CampaignPerformance]:
    return db.query(CampaignPerformance).all()


def get_by_id(db: Session, performance_id: int) -> CampaignPerformance:
    performance = db.query(CampaignPerformance).filter(CampaignPerformance.performance_id == performance_id).first()
    if not performance:
        raise ValueError(f"Campaign performance record not found with id: {performance_id}")
    return performance


def get_by_campaign(db: Session, campaign_id: int) -> list[CampaignPerformance]:
    marketing_campaign_service.get_by_id(db, campaign_id)
    return db.query(CampaignPerformance).filter(CampaignPerformance.campaign_id == campaign_id).all()


def create(db: Session, performance: CampaignPerformanceCreate) -> CampaignPerformance:
    marketing_campaign_service.get_by_id(db, performance.campaign_id)
    db_performance = CampaignPerformance(**performance.model_dump())
    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)
    return db_performance


def update(db: Session, performance_id: int, performance_update: CampaignPerformanceCreate) -> CampaignPerformance:
    performance = get_by_id(db, performance_id)
    for key, value in performance_update.model_dump().items():
        setattr(performance, key, value)
    db.commit()
    db.refresh(performance)
    return performance


def delete(db: Session, performance_id: int) -> None:
    performance = get_by_id(db, performance_id)
    db.delete(performance)
    db.commit()
