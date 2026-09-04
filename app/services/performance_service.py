from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Franchise, Outlet, Sale
from app.schemas import (
    DashboardSummaryDTO,
    FranchiseComparisonDTO,
    OutletPerformanceDTO,
    RevenueTrendDTO,
    UnderperformingOutletDTO,
)

UNDERPERFORMANCE_THRESHOLD = Decimal("0.70")


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_date_range(start_date: Optional[date], end_date: Optional[date]) -> tuple[date, date]:
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    return start_date, end_date


def _sum_sales(sales: list[Sale]) -> tuple[Decimal, int]:
    total_revenue = Decimal("0.00")
    total_transactions = 0
    for sale in sales:
        if sale.revenue:
            total_revenue += _to_decimal(sale.revenue)
        if sale.transaction_count:
            total_transactions += sale.transaction_count
    return total_revenue, total_transactions


def _compute_franchise_average_revenue(
    db: Session, franchise_id: int, start_date: date, end_date: date
) -> Decimal:
    outlets = db.query(Outlet).filter(Outlet.franchise_id == franchise_id).all()
    if not outlets:
        return Decimal("0.00")

    total = Decimal("0.00")
    for outlet in outlets:
        sales = (
            db.query(Sale)
            .filter(
                Sale.outlet_id == outlet.outlet_id,
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
            )
            .all()
        )
        revenue, _ = _sum_sales(sales)
        total += revenue

    return (total / len(outlets)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _compute_health_score(
    outlet: Outlet,
    revenue: Decimal,
    transactions: int,
    franchise_average: Decimal,
) -> Decimal:
    if franchise_average <= 0:
        return Decimal("0.00")

    score = (revenue / franchise_average) * Decimal("100")
    score = min(score, Decimal("100.00"))

    if outlet.status and outlet.status.lower() != "active":
        score = (score * Decimal("0.50")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_performance_label(health_score: Decimal) -> str:
    if health_score >= Decimal("80"):
        return "Excellent"
    elif health_score >= Decimal("60"):
        return "Good"
    elif health_score >= Decimal("40"):
        return "Average"
    elif health_score >= Decimal("20"):
        return "Underperforming"
    else:
        return "Critical"


def _get_sales_in_range(
    db: Session, outlet_id: int, start_date: date, end_date: date
) -> list[Sale]:
    return (
        db.query(Sale)
        .filter(
            Sale.outlet_id == outlet_id,
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
        )
        .all()
    )


def _build_revenue_trend(
    db: Session, outlet_id: int, start_date: date, end_date: date
) -> list[RevenueTrendDTO]:
    rows = (
        db.query(Sale.sale_date, func.sum(Sale.revenue), func.sum(Sale.transaction_count))
        .filter(
            Sale.outlet_id == outlet_id,
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
        )
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date)
        .all()
    )

    return [
        RevenueTrendDTO(
            date=row[0],
            revenue=_to_decimal(row[1]),
            transactions=int(row[2] or 0),
        )
        for row in rows
    ]


def get_outlet_performance(
    db: Session,
    outlet_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> OutletPerformanceDTO:
    outlet = db.query(Outlet).filter(Outlet.outlet_id == outlet_id).first()
    if not outlet:
        raise ValueError(f"Outlet not found with id: {outlet_id}")

    start_date, end_date = _get_date_range(start_date, end_date)
    sales = _get_sales_in_range(db, outlet_id, start_date, end_date)
    total_revenue, total_transactions = _sum_sales(sales)

    day_count = max(1, (end_date - start_date).days + 1)
    average_revenue_per_day = (total_revenue / day_count).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    average_revenue_per_transaction = (
        (total_revenue / total_transactions).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if total_transactions > 0
        else Decimal("0.00")
    )

    franchise_average = _compute_franchise_average_revenue(
        db, outlet.franchise_id, start_date, end_date
    )
    health_score = _compute_health_score(outlet, total_revenue, total_transactions, franchise_average)
    performance_label = _get_performance_label(health_score)

    revenue_trend = _build_revenue_trend(db, outlet_id, start_date, end_date)

    return OutletPerformanceDTO(
        outlet_id=outlet.outlet_id,
        outlet_name=outlet.outlet_name,
        location=outlet.location,
        status=outlet.status,
        franchise_id=outlet.franchise_id,
        franchise_name=outlet.franchise.franchise_name if outlet.franchise else None,
        total_revenue=total_revenue,
        total_transactions=total_transactions,
        average_revenue_per_day=average_revenue_per_day,
        average_revenue_per_transaction=average_revenue_per_transaction,
        health_score=health_score,
        performance_label=performance_label,
        revenue_trend=revenue_trend,
    )


def compare_outlets_in_franchise(
    db: Session,
    franchise_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[FranchiseComparisonDTO]:
    start_date, end_date = _get_date_range(start_date, end_date)
    outlets = db.query(Outlet).filter(Outlet.franchise_id == franchise_id).all()

    comparisons: list[FranchiseComparisonDTO] = []
    for outlet in outlets:
        sales = _get_sales_in_range(db, outlet.outlet_id, start_date, end_date)
        total_revenue, total_transactions = _sum_sales(sales)
        franchise_average = _compute_franchise_average_revenue(
            db, franchise_id, start_date, end_date
        )
        health_score = _compute_health_score(outlet, total_revenue, total_transactions, franchise_average)
        performance_label = _get_performance_label(health_score)

        comparisons.append(
            FranchiseComparisonDTO(
                outlet_id=outlet.outlet_id,
                outlet_name=outlet.outlet_name,
                location=outlet.location,
                status=outlet.status,
                total_revenue=total_revenue,
                total_transactions=total_transactions,
                health_score=health_score,
                performance_label=performance_label,
            )
        )

    comparisons.sort(key=lambda x: x.total_revenue, reverse=True)
    for index, comparison in enumerate(comparisons, start=1):
        comparison.rank = index

    return comparisons


def get_dashboard_summary(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> DashboardSummaryDTO:
    start_date, end_date = _get_date_range(start_date, end_date)
    outlets = db.query(Outlet).all()

    comparisons: list[FranchiseComparisonDTO] = []
    total_revenue = Decimal("0.00")
    total_transactions = 0
    score_sum = Decimal("0.00")
    active_count = 0
    underperforming_count = 0

    for outlet in outlets:
        sales = _get_sales_in_range(db, outlet.outlet_id, start_date, end_date)
        outlet_revenue, outlet_transactions = _sum_sales(sales)
        franchise_average = _compute_franchise_average_revenue(
            db, outlet.franchise_id, start_date, end_date
        )
        health_score = _compute_health_score(
            outlet, outlet_revenue, outlet_transactions, franchise_average
        )
        performance_label = _get_performance_label(health_score)

        comparisons.append(
            FranchiseComparisonDTO(
                outlet_id=outlet.outlet_id,
                outlet_name=outlet.outlet_name,
                location=outlet.location,
                status=outlet.status,
                total_revenue=outlet_revenue,
                total_transactions=outlet_transactions,
                health_score=health_score,
                performance_label=performance_label,
            )
        )

        total_revenue += outlet_revenue
        total_transactions += outlet_transactions
        score_sum += health_score

        if outlet.status and outlet.status.lower() == "active":
            active_count += 1
        if performance_label == "Underperforming" or performance_label == "Critical":
            underperforming_count += 1

    comparisons.sort(key=lambda x: x.total_revenue, reverse=True)

    average_health_score = (
        (score_sum / len(comparisons)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if comparisons
        else Decimal("0.00")
    )

    top = comparisons[0] if comparisons else None
    lowest = comparisons[-1] if comparisons else None
    underperformers = [c for c in comparisons if c.performance_label in ("Underperforming", "Critical")][:5]

    return DashboardSummaryDTO(
        total_outlets=len(outlets),
        active_outlets=active_count,
        underperforming_outlets=underperforming_count,
        total_revenue=total_revenue,
        total_transactions=total_transactions,
        average_health_score=average_health_score,
        top_performing_outlet=top,
        lowest_performing_outlet=lowest,
        recent_underperformers=underperformers,
    )


def get_underperforming_outlets(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[UnderperformingOutletDTO]:
    start_date, end_date = _get_date_range(start_date, end_date)
    outlets = db.query(Outlet).all()

    underperformers: list[UnderperformingOutletDTO] = []
    for outlet in outlets:
        sales = _get_sales_in_range(db, outlet.outlet_id, start_date, end_date)
        total_revenue, total_transactions = _sum_sales(sales)
        franchise_average = _compute_franchise_average_revenue(
            db, outlet.franchise_id, start_date, end_date
        )
        health_score = _compute_health_score(
            outlet, total_revenue, total_transactions, franchise_average
        )

        if franchise_average > 0 and total_revenue < franchise_average * UNDERPERFORMANCE_THRESHOLD:
            underperformers.append(
                UnderperformingOutletDTO(
                    outlet_id=outlet.outlet_id,
                    outlet_name=outlet.outlet_name,
                    location=outlet.location,
                    franchise_id=outlet.franchise_id,
                    franchise_name=outlet.franchise.franchise_name if outlet.franchise else None,
                    total_revenue=total_revenue,
                    franchise_average_revenue=franchise_average,
                    health_score=health_score,
                    reason="Revenue is below 70% of the franchise average for the selected period.",
                )
            )

    underperformers.sort(key=lambda x: x.health_score)
    return underperformers
