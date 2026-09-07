from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    DemandForecastDTO,
    InventoryDashboardDTO,
    InventoryStatusDTO,
    ReplenishmentRecommendationDTO,
    StockAlertDTO,
)
from app.services import inventory_analytics_service

router = APIRouter(prefix="/api/inventory/dashboard", tags=["Inventory Dashboard"])


@router.get("/summary", response_model=InventoryDashboardDTO)
def get_inventory_dashboard_summary(db: Session = Depends(get_db)):
    return inventory_analytics_service.get_dashboard_summary(db)


@router.get("/status", response_model=list[InventoryStatusDTO])
def get_inventory_status(db: Session = Depends(get_db)):
    return inventory_analytics_service.get_inventory_status(db)


@router.get("/alerts", response_model=list[StockAlertDTO])
def get_stock_alerts(db: Session = Depends(get_db)):
    return inventory_analytics_service.get_stock_alerts(db)


@router.get("/replenishment", response_model=list[ReplenishmentRecommendationDTO])
def get_replenishment_recommendations(db: Session = Depends(get_db)):
    return inventory_analytics_service.get_replenishment_recommendations(db)


@router.get("/forecast/{outlet_id}/{product_id}", response_model=DemandForecastDTO)
def get_demand_forecast(outlet_id: int, product_id: int, db: Session = Depends(get_db)):
    try:
        return inventory_analytics_service.forecast_demand(db, outlet_id, product_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
