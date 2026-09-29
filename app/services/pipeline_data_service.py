"""Build pandas inputs for ``data_engine.pipeline`` from SQLAlchemy models."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    Attendance,
    AuditComplianceRecord,
    Employee,
    Inventory,
    InventoryTransaction,
    MarketingCampaign,
    CampaignPerformance,
    Sale,
    Schedule,
)
from app.utils.outlet_id import format_pipeline_outlet_id


def _days_back(default: int = 60) -> tuple[date, date]:
    end = date.today()
    start = end - timedelta(days=default)
    return start, end


def build_sales_dataframe(db: Session, start: date | None = None, end: date | None = None) -> pd.DataFrame:
    if start is None or end is None:
        start, end = _days_back()
    rows = (
        db.query(Sale.outlet_id, Sale.sale_date, Sale.revenue)
        .filter(Sale.sale_date >= start, Sale.sale_date <= end)
        .all()
    )
    if not rows:
        return pd.DataFrame(columns=["outlet_id", "date", "revenue"])
    data = [
        {
            "outlet_id": format_pipeline_outlet_id(r.outlet_id),
            "date": r.sale_date.isoformat(),
            "revenue": float(r.revenue or 0),
        }
        for r in rows
    ]
    return pd.DataFrame(data)


def build_inventory_dataframe(db: Session, start: date | None = None, end: date | None = None) -> pd.DataFrame:
    if start is None or end is None:
        start, end = _days_back()

    tx_rows = (
        db.query(
            Inventory.outlet_id,
            InventoryTransaction.transaction_date,
            InventoryTransaction.transaction_type,
            func.coalesce(func.sum(InventoryTransaction.quantity), 0).label("qty"),
        )
        .join(Inventory, Inventory.inventory_id == InventoryTransaction.inventory_id)
        .filter(
            InventoryTransaction.transaction_date >= start,
            InventoryTransaction.transaction_date <= end,
        )
        .group_by(
            Inventory.outlet_id,
            InventoryTransaction.transaction_date,
            InventoryTransaction.transaction_type,
        )
        .all()
    )

    by_outlet_date: dict[tuple[int, date], dict[str, float]] = defaultdict(
        lambda: {"received_qty": 0.0, "consumed_qty": 0.0, "wastage_qty": 0.0}
    )
    for outlet_id, tx_date, tx_type, qty in tx_rows:
        key = (outlet_id, tx_date)
        amount = float(qty or 0)
        tx = (tx_type or "").upper()
        if tx == "IN":
            by_outlet_date[key]["received_qty"] += amount
        elif tx == "WASTAGE":
            by_outlet_date[key]["wastage_qty"] += amount
        elif tx in ("OUT", "RETURN"):
            by_outlet_date[key]["consumed_qty"] += amount

    rows: list[dict] = []
    opening_by_outlet: dict[int, float] = defaultdict(lambda: 500.0)
    for (outlet_id, tx_date), flows in sorted(by_outlet_date.items(), key=lambda x: (x[0][0], x[0][1])):
        opening = opening_by_outlet[outlet_id]
        received = flows["received_qty"]
        consumed = flows["consumed_qty"]
        wastage = flows["wastage_qty"]
        closing = opening + received - consumed - wastage
        rows.append(
            {
                "outlet_id": format_pipeline_outlet_id(outlet_id),
                "date": tx_date.isoformat(),
                "opening_stock": round(opening, 2),
                "received_qty": round(received, 2),
                "consumed_qty": round(consumed, 2),
                "wastage_qty": round(wastage, 2),
                "closing_stock": round(closing, 2),
            }
        )
        opening_by_outlet[outlet_id] = max(0.0, closing)

    if not rows:
        return pd.DataFrame(
            columns=[
                "outlet_id",
                "date",
                "opening_stock",
                "received_qty",
                "consumed_qty",
                "wastage_qty",
                "closing_stock",
            ]
        )
    return pd.DataFrame(rows)


def build_staff_dataframe(db: Session, start: date | None = None, end: date | None = None) -> pd.DataFrame:
    if start is None or end is None:
        start, end = _days_back()

    schedule_rows = (
        db.query(Employee.outlet_id, Schedule.schedule_date, func.count(Schedule.schedule_id))
        .join(Schedule, Schedule.employee_id == Employee.employee_id)
        .filter(
            Schedule.schedule_date >= start,
            Schedule.schedule_date <= end,
            Schedule.status.in_(["SCHEDULED", "COMPLETED"]),
        )
        .group_by(Employee.outlet_id, Schedule.schedule_date)
        .all()
    )

    present_rows = (
        db.query(Employee.outlet_id, Attendance.attendance_date, func.count(Attendance.attendance_id))
        .join(Attendance, Attendance.employee_id == Employee.employee_id)
        .filter(
            Attendance.attendance_date >= start,
            Attendance.attendance_date <= end,
            Attendance.status.in_(["PRESENT", "LATE", "HALF_DAY"]),
        )
        .group_by(Employee.outlet_id, Attendance.attendance_date)
        .all()
    )

    scheduled_map = {(o, d): int(c) for o, d, c in schedule_rows}
    present_map = {(o, d): int(c) for o, d, c in present_rows}
    all_keys = set(scheduled_map.keys()) | set(present_map.keys())

    rows: list[dict] = []
    for outlet_id, day in sorted(all_keys):
        scheduled = scheduled_map.get((outlet_id, day), 0)
        present = present_map.get((outlet_id, day), 0)
        if scheduled == 0 and present > 0:
            scheduled = present
        absent = max(0, scheduled - present)
        is_peak = day.weekday() in (4, 5) and present < scheduled
        rows.append(
            {
                "outlet_id": format_pipeline_outlet_id(outlet_id),
                "date": day.isoformat(),
                "scheduled": scheduled,
                "present": present,
                "absent": absent,
                "is_peak_understaffed": bool(is_peak),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=["outlet_id", "date", "scheduled", "present", "absent", "is_peak_understaffed"]
        )
    return pd.DataFrame(rows)


def build_marketing_dataframe(db: Session) -> pd.DataFrame:
    campaigns = db.query(MarketingCampaign).all()
    rows: list[dict] = []
    for campaign in campaigns:
        perf = (
            db.query(
                func.coalesce(func.sum(CampaignPerformance.revenue), 0),
            )
            .filter(CampaignPerformance.campaign_id == campaign.campaign_id)
            .scalar()
        )
        cost = float(campaign.budget or 0)
        revenue = float(perf or 0)
        roi = ((revenue - cost) / cost * 100) if cost > 0 else 0.0
        rows.append(
            {
                "outlet_id": format_pipeline_outlet_id(campaign.outlet_id),
                "campaign_cost": round(cost, 2),
                "revenue_attributed": round(revenue, 2),
                "roi": round(roi, 2),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["outlet_id", "campaign_cost", "revenue_attributed", "roi"])
    return pd.DataFrame(rows)


def build_audit_dataframe(db: Session, start: date | None = None, end: date | None = None) -> pd.DataFrame:
    if start is None or end is None:
        start, end = _days_back(365)
    records = (
        db.query(AuditComplianceRecord)
        .filter(AuditComplianceRecord.record_date >= start, AuditComplianceRecord.record_date <= end)
        .order_by(AuditComplianceRecord.record_date)
        .all()
    )
    if not records:
        return pd.DataFrame(columns=["outlet_id", "compliance_score", "violation_count"])
    rows = [
        {
            "outlet_id": format_pipeline_outlet_id(r.outlet_id),
            "compliance_score": float(r.compliance_score),
            "violation_count": int(r.violation_count or 0),
        }
        for r in records
    ]
    return pd.DataFrame(rows)


def build_all_pipeline_inputs(db: Session) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        build_sales_dataframe(db),
        build_inventory_dataframe(db),
        build_staff_dataframe(db),
        build_marketing_dataframe(db),
        build_audit_dataframe(db),
    )
