from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Inventory, InventoryTransaction, Outlet, Product
from app.schemas import (
    DemandForecastDTO,
    InventoryDashboardDTO,
    InventoryStatusDTO,
    ReplenishmentRecommendationDTO,
    StockAlertDTO,
)
from app.services import inventory_service


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_status(current_stock: Decimal, reorder_point: Decimal, max_stock: Optional[Decimal]) -> str:
    if current_stock <= 0:
        return "Critical"
    if current_stock <= reorder_point:
        return "Low Stock"
    if max_stock is not None and current_stock >= max_stock:
        return "Overstock"
    return "Normal"


def _get_date_range(days: int) -> tuple[date, date]:
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def forecast_demand(
    db: Session,
    outlet_id: int,
    product_id: int,
    days: int = 30,
) -> DemandForecastDTO:
    inventory = inventory_service.get_by_outlet_and_product(db, outlet_id, product_id)
    if not inventory:
        raise ValueError(f"Inventory not found for outlet {outlet_id} and product {product_id}")

    start_date, end_date = _get_date_range(days)

    total_demand = (
        db.query(func.coalesce(func.sum(InventoryTransaction.quantity), 0))
        .filter(
            InventoryTransaction.inventory_id == inventory.inventory_id,
            InventoryTransaction.transaction_type == "OUT",
            InventoryTransaction.transaction_date >= start_date,
            InventoryTransaction.transaction_date <= end_date,
        )
        .scalar()
    )

    total_demand = _to_decimal(total_demand)
    forecasted_daily = (total_demand / Decimal(days)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    outlet = db.query(Outlet).filter(Outlet.outlet_id == outlet_id).first()
    product = db.query(Product).filter(Product.product_id == product_id).first()

    return DemandForecastDTO(
        outlet_id=outlet_id,
        outlet_name=outlet.outlet_name if outlet else None,
        product_id=product_id,
        product_name=product.product_name if product else None,
        forecasted_daily_demand=forecasted_daily,
        forecast_period_days=days,
        total_historical_demand=total_demand,
    )


def get_inventory_status(db: Session) -> list[InventoryStatusDTO]:
    inventory_items = db.query(Inventory).all()
    result = []
    for item in inventory_items:
        current_stock = _to_decimal(item.current_stock)
        reorder_point = _to_decimal(item.reorder_point)
        max_stock = _to_decimal(item.max_stock) if item.max_stock is not None else None

        status = _get_status(current_stock, reorder_point, max_stock)

        result.append(
            InventoryStatusDTO(
                inventory_id=item.inventory_id,
                outlet_id=item.outlet_id,
                outlet_name=item.outlet.outlet_name if item.outlet else None,
                product_id=item.product_id,
                product_name=item.product.product_name if item.product else None,
                category=item.product.category if item.product else None,
                current_stock=current_stock,
                reorder_point=reorder_point,
                reorder_quantity=_to_decimal(item.reorder_quantity),
                max_stock=max_stock,
                status=status,
            )
        )
    return result


def get_stock_alerts(db: Session) -> list[StockAlertDTO]:
    alerts = []
    for item in get_inventory_status(db):
        if item.status == "Critical":
            alerts.append(
                StockAlertDTO(
                    alert_type="CRITICAL",
                    outlet_id=item.outlet_id,
                    outlet_name=item.outlet_name,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    current_stock=item.current_stock,
                    threshold=Decimal("0.00"),
                    message=f"{item.product_name} is out of stock at {item.outlet_name}",
                )
            )
        elif item.status == "Low Stock":
            alerts.append(
                StockAlertDTO(
                    alert_type="LOW_STOCK",
                    outlet_id=item.outlet_id,
                    outlet_name=item.outlet_name,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    current_stock=item.current_stock,
                    threshold=item.reorder_point,
                    message=f"{item.product_name} is below reorder point at {item.outlet_name}",
                )
            )
        elif item.status == "Overstock":
            alerts.append(
                StockAlertDTO(
                    alert_type="OVERSTOCK",
                    outlet_id=item.outlet_id,
                    outlet_name=item.outlet_name,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    current_stock=item.current_stock,
                    threshold=item.max_stock or Decimal("0.00"),
                    message=f"{item.product_name} is overstocked at {item.outlet_name}",
                )
            )
    return alerts


def _calculate_recommendation(
    inventory: Inventory,
    forecast: DemandForecastDTO,
    lead_time_days: int = 3,
    safety_stock_days: int = 2,
) -> Optional[ReplenishmentRecommendationDTO]:
    current_stock = _to_decimal(inventory.current_stock)
    reorder_point = _to_decimal(inventory.reorder_point)
    reorder_quantity = _to_decimal(inventory.reorder_quantity)
    forecasted_daily = forecast.forecasted_daily_demand

    if forecasted_daily <= 0 and current_stock > reorder_point:
        return None

    if current_stock <= reorder_point or current_stock <= 0:
        safety_stock = (forecasted_daily * Decimal(safety_stock_days)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        required_during_lead_time = (forecasted_daily * Decimal(lead_time_days)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        target_stock = required_during_lead_time + safety_stock

        needed = target_stock - current_stock
        recommended_quantity = max(needed, reorder_quantity)
        recommended_quantity = recommended_quantity.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        days_until_stockout = None
        if forecasted_daily > 0:
            days_until_stockout = int((current_stock / forecasted_daily).to_integral_value(rounding=ROUND_HALF_UP))

        return ReplenishmentRecommendationDTO(
            outlet_id=inventory.outlet_id,
            outlet_name=inventory.outlet.outlet_name if inventory.outlet else None,
            product_id=inventory.product_id,
            product_name=inventory.product.product_name if inventory.product else None,
            current_stock=current_stock,
            forecasted_daily_demand=forecasted_daily,
            days_until_stockout=days_until_stockout,
            recommended_order_quantity=recommended_quantity,
            recommended_order_date=date.today(),
            reason=f"Stock is at or below reorder point ({reorder_point}). Reorder to cover lead time + safety stock.",
        )
    return None


def get_replenishment_recommendations(
    db: Session,
    lead_time_days: int = 3,
    safety_stock_days: int = 2,
) -> list[ReplenishmentRecommendationDTO]:
    recommendations = []
    inventory_items = db.query(Inventory).all()

    for inventory in inventory_items:
        try:
            forecast = forecast_demand(db, inventory.outlet_id, inventory.product_id, days=30)
            recommendation = _calculate_recommendation(inventory, forecast, lead_time_days, safety_stock_days)
            if recommendation:
                recommendations.append(recommendation)
        except ValueError:
            continue

    return recommendations


def get_dashboard_summary(db: Session) -> InventoryDashboardDTO:
    total_products = db.query(Product).count()
    inventory_items = db.query(Inventory).all()

    total_stock_value = Decimal("0.00")
    low_stock_count = 0
    critical_stock_count = 0
    overstock_count = 0

    for item in inventory_items:
        current_stock = _to_decimal(item.current_stock)
        unit_price = _to_decimal(item.product.unit_price) if item.product else Decimal("0.00")
        total_stock_value += current_stock * unit_price

        status = _get_status(
            current_stock,
            _to_decimal(item.reorder_point),
            _to_decimal(item.max_stock) if item.max_stock is not None else None,
        )
        if status == "Low Stock":
            low_stock_count += 1
        elif status == "Critical":
            critical_stock_count += 1
        elif status == "Overstock":
            overstock_count += 1

    start_date, end_date = _get_date_range(30)
    total_wastage = (
        db.query(func.coalesce(func.sum(InventoryTransaction.quantity), 0))
        .filter(
            InventoryTransaction.transaction_type == "WASTAGE",
            InventoryTransaction.transaction_date >= start_date,
            InventoryTransaction.transaction_date <= end_date,
        )
        .scalar()
    )

    alerts = get_stock_alerts(db)
    recommendations = get_replenishment_recommendations(db)

    return InventoryDashboardDTO(
        total_products=total_products,
        total_inventory_items=len(inventory_items),
        total_stock_value=total_stock_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        low_stock_count=low_stock_count,
        critical_stock_count=critical_stock_count,
        overstock_count=overstock_count,
        total_wastage_30_days=_to_decimal(total_wastage),
        top_alerts=alerts[:10],
        replenishment_recommendations=recommendations[:10],
    )
