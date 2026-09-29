from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ActionPlanCreate, ActionPlanResponse, NotificationResponse, NotificationStatusUpdate
from app.services import notification_service

router = APIRouter(prefix="/api/notifications", tags=["Notifications & Workflow"])


@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return notification_service.list_notifications(db, status)


@router.post("/sync", response_model=dict)
def sync_notifications(db: Session = Depends(get_db)):
    count = notification_service.sync_alerts_from_agents(db)
    return {"synced": count}


@router.patch("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    payload: NotificationStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        return notification_service.update_notification_status(db, notification_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/action-plans", response_model=list[ActionPlanResponse])
def list_action_plans(
    outlet_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return notification_service.list_action_plans(db, outlet_id)


@router.post("/action-plans", response_model=ActionPlanResponse, status_code=status.HTTP_201_CREATED)
def create_action_plan(payload: ActionPlanCreate, db: Session = Depends(get_db)):
    try:
        return notification_service.create_action_plan(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
