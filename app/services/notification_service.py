from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import ActionPlan, Notification, Outlet
from app.schemas import ActionPlanCreate, NotificationStatusUpdate
from app.services import intelligence_service, inventory_analytics_service, workforce_analytics_service
from app.utils.outlet_id import parse_pipeline_outlet_id


def _outlet_name(db: Session, outlet_id: int | None) -> str | None:
    if outlet_id is None:
        return None
    outlet = db.query(Outlet).filter(Outlet.outlet_id == outlet_id).first()
    return outlet.outlet_name if outlet else None


def _attach(row: Notification) -> dict:
    data = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    return data


def list_notifications(db: Session, status: str | None = None) -> list[dict]:
    q = db.query(Notification).order_by(Notification.created_at.desc())
    if status:
        q = q.filter(Notification.status == status)
    rows = q.all()
    return [_attach(r) | {"outlet_name": _outlet_name(db, r.outlet_id)} for r in rows]


def update_notification_status(db: Session, notification_id: int, payload: NotificationStatusUpdate) -> dict:
    row = db.query(Notification).filter(Notification.notification_id == notification_id).first()
    if not row:
        raise ValueError(f"Notification {notification_id} not found")
    row.status = payload.status
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return _attach(row) | {"outlet_name": _outlet_name(db, row.outlet_id)}


def _upsert_notification(db: Session, **fields) -> Notification:
    existing = db.query(Notification).filter(Notification.alert_key == fields["alert_key"]).first()
    now = datetime.utcnow()
    if existing:
        for key, value in fields.items():
            if key != "alert_key":
                setattr(existing, key, value)
        existing.updated_at = now
        db.commit()
        db.refresh(existing)
        return existing
    row = Notification(**fields, created_at=now, updated_at=now)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def sync_alerts_from_agents(db: Session) -> int:
    """Refresh notification rows from inventory, workforce, and intelligence root causes."""
    count = 0

    for alert in inventory_analytics_service.get_stock_alerts(db):
        key = f"inv-alert-{alert.outlet_id}-{alert.product_id}"
        sev = "critical" if alert.alert_type == "CRITICAL" else "high" if alert.alert_type == "LOW_STOCK" else "medium"
        _upsert_notification(
            db,
            alert_key=key,
            domain="Inventory",
            severity=sev,
            outlet_id=alert.outlet_id,
            title=f"{alert.alert_type}: {alert.product_name or 'Product'}",
            description=alert.message,
            status="active",
            source_agent="Inventory Replenishment Agent",
            affected_area="Stock / Replenishment",
            metric="current_stock",
            metric_value=Decimal(str(alert.current_stock)),
            threshold_value=Decimal(str(alert.threshold)),
            recommendation="Review replenishment and reallocate buffer stock if needed.",
        )
        count += 1

    for alert in workforce_analytics_service.get_all_staffing_alerts(db):
        key = f"staff-alert-{alert.outlet_id}-{alert.alert_type}-{alert.scheduled_staff_count}"
        sev = "high" if alert.alert_type == "SHORTAGE" else "medium"
        _upsert_notification(
            db,
            alert_key=key,
            domain="Workforce",
            severity=sev,
            outlet_id=alert.outlet_id,
            title=f"Staffing {alert.alert_type}",
            description=alert.message,
            status="active",
            source_agent="Workforce Dispatch Agent",
            affected_area="Shift roster",
            metric="scheduled_staff_count",
            metric_value=Decimal(str(alert.scheduled_staff_count)),
            threshold_value=Decimal(str(alert.expected_staff_count)),
            recommendation="Adjust schedules or call backup staff for peak coverage.",
        )
        count += 1

    pipeline = intelligence_service.get_latest(db)
    for rc in pipeline.root_causes:
        if not rc.issues:
            continue
        oid = parse_pipeline_outlet_id(rc.outlet_id)
        top = rc.issues[0]
        key = f"pipeline-rc-{rc.outlet_id}-{top.metric}"
        sev = top.severity if top.severity in ("critical", "high", "medium", "low") else "medium"
        _upsert_notification(
            db,
            alert_key=key,
            domain="Pipeline" if top.domain != "Audit" else "Audit",
            severity=sev,
            outlet_id=oid,
            title=rc.priority_issue or top.finding,
            description=top.finding,
            status="active",
            source_agent="Franchise Intelligence Engine",
            affected_area=top.domain,
            metric=top.metric,
            metric_value=Decimal(str(top.value)) if top.value is not None else None,
            threshold_value=Decimal(str(top.threshold)) if top.threshold is not None else None,
            recommendation=rc.overall_recommendation,
        )
        count += 1

    return count


def create_action_plan(db: Session, payload: ActionPlanCreate) -> dict:
    if not db.query(Outlet).filter(Outlet.outlet_id == payload.outlet_id).first():
        raise ValueError(f"Outlet {payload.outlet_id} not found")
    row = ActionPlan(**payload.model_dump(), created_at=datetime.utcnow())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        c.name: getattr(row, c.name)
        for c in row.__table__.columns
    } | {"outlet_name": _outlet_name(db, row.outlet_id)}


def list_action_plans(db: Session, outlet_id: int | None = None) -> list[dict]:
    q = db.query(ActionPlan).order_by(ActionPlan.created_at.desc())
    if outlet_id is not None:
        q = q.filter(ActionPlan.outlet_id == outlet_id)
    rows = q.all()
    return [
        {c.name: getattr(r, c.name) for c in r.__table__.columns}
        | {"outlet_name": _outlet_name(db, r.outlet_id)}
        for r in rows
    ]
