from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import CampaignPerformance, MarketingCampaign, Outlet
from app.schemas import CampaignAnalyticsDTO, MarketingDashboardDTO


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_performance_label(roi: Decimal, engagement_rate: Decimal) -> str:
    if roi >= Decimal("50") and engagement_rate >= Decimal("5"):
        return "Excellent"
    elif roi >= Decimal("20") and engagement_rate >= Decimal("3"):
        return "Good"
    elif roi >= Decimal("0") and engagement_rate >= Decimal("1"):
        return "Average"
    elif roi < Decimal("0"):
        return "Underperforming"
    else:
        return "Poor"


def analyze_campaign(db: Session, campaign_id: int) -> CampaignAnalyticsDTO:
    campaign = db.query(MarketingCampaign).filter(MarketingCampaign.campaign_id == campaign_id).first()
    if not campaign:
        raise ValueError(f"Campaign not found with id: {campaign_id}")

    performances = db.query(CampaignPerformance).filter(CampaignPerformance.campaign_id == campaign_id).all()

    total_revenue = sum(_to_decimal(p.revenue) for p in performances)
    total_impressions = sum(p.impressions or 0 for p in performances)
    total_clicks = sum(p.clicks or 0 for p in performances)
    total_conversions = sum(p.conversions or 0 for p in performances)
    avg_engagement = (
        (sum(_to_decimal(p.engagement_score) for p in performances) / len(performances)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if performances
        else Decimal("0.00")
    )

    budget = _to_decimal(campaign.budget)
    roi = (
        ((total_revenue - budget) / budget * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if budget > 0
        else Decimal("0.00")
    )

    engagement_rate = (
        (Decimal(total_clicks) / Decimal(total_impressions) * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if total_impressions > 0
        else Decimal("0.00")
    )

    conversion_rate = (
        (Decimal(total_conversions) / Decimal(total_clicks) * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if total_clicks > 0
        else Decimal("0.00")
    )

    outlet_name = campaign.outlet.outlet_name if campaign.outlet else None

    return CampaignAnalyticsDTO(
        campaign_id=campaign.campaign_id,
        campaign_name=campaign.campaign_name,
        outlet_id=campaign.outlet_id,
        outlet_name=outlet_name,
        campaign_type=campaign.campaign_type,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        budget=budget,
        total_revenue=total_revenue,
        total_impressions=total_impressions,
        total_clicks=total_clicks,
        total_conversions=total_conversions,
        average_engagement_score=avg_engagement,
        roi_percentage=roi,
        engagement_rate=engagement_rate,
        conversion_rate=conversion_rate,
        status=campaign.status or "Unknown",
        performance_label=_get_performance_label(roi, engagement_rate),
    )


def get_all_campaign_analytics(db: Session) -> list[CampaignAnalyticsDTO]:
    campaigns = db.query(MarketingCampaign).all()
    return [analyze_campaign(db, c.campaign_id) for c in campaigns]


def get_marketing_dashboard(db: Session) -> MarketingDashboardDTO:
    campaigns = db.query(MarketingCampaign).all()
    active_campaigns = [c for c in campaigns if c.status and c.status.upper() == "ACTIVE"]

    analytics = [analyze_campaign(db, c.campaign_id) for c in campaigns]

    total_budget = sum(a.budget for a in analytics)
    total_revenue = sum(a.total_revenue for a in analytics)

    overall_roi = (
        ((total_revenue - total_budget) / total_budget * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if total_budget > 0
        else Decimal("0.00")
    )

    avg_engagement = (
        (sum(a.engagement_rate for a in analytics) / len(analytics)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if analytics
        else Decimal("0.00")
    )

    avg_conversion = (
        (sum(a.conversion_rate for a in analytics) / len(analytics)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if analytics
        else Decimal("0.00")
    )

    sorted_analytics = sorted(analytics, key=lambda a: a.roi_percentage, reverse=True)
    top_campaigns = sorted_analytics[:5]
    underperforming = [a for a in analytics if a.performance_label in ("Underperforming", "Poor")]

    campaigns_by_type = {}
    for a in analytics:
        campaigns_by_type[a.campaign_type or "Unknown"] = campaigns_by_type.get(a.campaign_type or "Unknown", 0) + 1

    return MarketingDashboardDTO(
        total_campaigns=len(campaigns),
        active_campaigns=len(active_campaigns),
        total_budget=total_budget,
        total_revenue=total_revenue,
        overall_roi_percentage=overall_roi,
        average_engagement_rate=avg_engagement,
        average_conversion_rate=avg_conversion,
        top_campaigns=top_campaigns,
        underperforming_campaigns=underperforming[:5],
        campaigns_by_type=campaigns_by_type,
    )
