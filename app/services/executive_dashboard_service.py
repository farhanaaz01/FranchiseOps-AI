from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models import ActionPlan, Notification, Outlet
from app.schemas import ExecutiveAgentSummaryDTO, ExecutiveDashboardDTO
from app.services import (
    audit_analytics_service,
    intelligence_service,
    inventory_analytics_service,
    marketing_analytics_service,
    performance_service,
    workforce_analytics_service,
)


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_executive_dashboard(db: Session) -> ExecutiveDashboardDTO:
    perf = performance_service.get_dashboard_summary(db)
    inv = inventory_analytics_service.get_dashboard_summary(db)
    workforce = workforce_analytics_service.get_workforce_dashboard(db)
    marketing = marketing_analytics_service.get_marketing_dashboard(db)
    audit_dash = audit_analytics_service.get_audit_dashboard(db)
    pipeline = intelligence_service.get_latest(db)

    healthy = at_risk = critical = 0
    for score in pipeline.performance_scores:
        if score.health_status == "Healthy":
            healthy += 1
        elif score.health_status == "At Risk":
            at_risk += 1
        else:
            critical += 1

    active_notifications = (
        db.query(Notification).filter(Notification.status.in_(["active", "acknowledged"])).count()
    )
    open_plans = db.query(ActionPlan).filter(ActionPlan.status.in_(["open", "in_progress"])).count()

    agent_summaries = [
        ExecutiveAgentSummaryDTO(
            agent_name="Outlet Performance Agent",
            status="active",
            key_metric="Network revenue (30d)",
            key_value=str(perf.total_revenue),
            alert_count=perf.underperforming_outlets,
        ),
        ExecutiveAgentSummaryDTO(
            agent_name="Inventory Replenishment Agent",
            status="active",
            key_metric="Stock alerts",
            key_value=str(len(inv.top_alerts)),
            alert_count=len(inv.top_alerts),
        ),
        ExecutiveAgentSummaryDTO(
            agent_name="Workforce Dispatch Agent",
            status="active",
            key_metric="Staffing alerts",
            key_value=str(len(workforce.staffing_alerts)),
            alert_count=len(workforce.staffing_alerts),
        ),
        ExecutiveAgentSummaryDTO(
            agent_name="Marketing ROI Agent",
            status="active",
            key_metric="Overall ROI %",
            key_value=str(marketing.overall_roi_percentage),
            alert_count=len(marketing.underperforming_campaigns),
        ),
        ExecutiveAgentSummaryDTO(
            agent_name="Audit & Compliance Agent",
            status="active",
            key_metric="Avg compliance score",
            key_value=str(audit_dash.average_compliance_score),
            alert_count=audit_dash.outlets_below_compliance_threshold,
        ),
        ExecutiveAgentSummaryDTO(
            agent_name="Franchise Intelligence Engine",
            status="active",
            key_metric="Outlets scored",
            key_value=str(pipeline.outlet_count),
            alert_count=sum(1 for rc in pipeline.root_causes if rc.issues),
        ),
    ]

    compliance = audit_analytics_service.get_compliance_summaries(db)
    top_priority = compliance[:5]

    total_outlets = db.query(Outlet).count()
    active_outlets = db.query(Outlet).filter(Outlet.status == "Active").count()

    return ExecutiveDashboardDTO(
        generated_at=datetime.utcnow(),
        total_outlets=total_outlets,
        active_outlets=active_outlets,
        total_revenue=_to_decimal(perf.total_revenue),
        average_health_score=_to_decimal(perf.average_health_score),
        critical_outlets=critical,
        at_risk_outlets=at_risk,
        healthy_outlets=healthy,
        active_notifications=active_notifications,
        open_action_plans=open_plans,
        pipeline_generated_at=pipeline.generated_at,
        agent_summaries=agent_summaries,
        top_priority_outlets=top_priority,
    )
