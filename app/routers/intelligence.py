from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from data_engine.schemas import ForecastResult, PipelineOutput, RootCauseFinding

from app.database import get_db
from app.services import intelligence_service, notification_service

router = APIRouter(prefix="/api/intelligence", tags=["Intelligence"])


@router.get("/latest", response_model=PipelineOutput)
def get_latest_intelligence(db: Session = Depends(get_db)):
    return intelligence_service.get_latest(db)


@router.post("/run", response_model=PipelineOutput)
def run_intelligence_pipeline(db: Session = Depends(get_db)):
    output = intelligence_service.run_pipeline(db)
    notification_service.sync_alerts_from_agents(db)
    return output


@router.get("/root-causes", response_model=list[RootCauseFinding])
def get_root_causes(
    outlet_id: str | None = Query(None, description="OUT-01 or numeric outlet id"),
    db: Session = Depends(get_db),
):
    return intelligence_service.get_root_causes(db, outlet_id)


@router.get("/forecasts", response_model=list[ForecastResult])
def get_forecasts(
    outlet_id: str | None = Query(None, description="OUT-01 or numeric outlet id"),
    db: Session = Depends(get_db),
):
    return intelligence_service.get_forecasts(db, outlet_id)
