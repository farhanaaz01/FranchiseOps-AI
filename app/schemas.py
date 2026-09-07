from datetime import date
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class FranchiseBase(BaseModel):
    franchise_name: str
    region: Optional[str] = None
    owner_name: Optional[str] = None


class FranchiseCreate(FranchiseBase):
    pass


class FranchiseResponse(FranchiseBase):
    model_config = ConfigDict(from_attributes=True)

    franchise_id: int


class OutletBase(BaseModel):
    outlet_name: str
    location: Optional[str] = None
    status: Optional[str] = "Active"


class OutletCreate(OutletBase):
    franchise_id: int


class OutletResponse(OutletBase):
    model_config = ConfigDict(from_attributes=True)

    outlet_id: int
    franchise_id: int


class SaleBase(BaseModel):
    sale_date: date
    revenue: Optional[Decimal] = Decimal("0.00")
    transaction_count: Optional[int] = 0


class SaleCreate(SaleBase):
    outlet_id: int


class SaleResponse(SaleBase):
    model_config = ConfigDict(from_attributes=True)

    sale_id: int
    outlet_id: int


class RevenueTrendDTO(BaseModel):
    date: date
    revenue: Decimal
    transactions: int


class OutletPerformanceDTO(BaseModel):
    outlet_id: int
    outlet_name: str
    location: Optional[str] = None
    status: Optional[str] = None
    franchise_id: int
    franchise_name: Optional[str] = None

    total_revenue: Decimal
    total_transactions: int
    average_revenue_per_day: Decimal
    average_revenue_per_transaction: Decimal

    health_score: Decimal
    performance_label: str
    revenue_trend: List[RevenueTrendDTO]


class FranchiseComparisonDTO(BaseModel):
    outlet_id: int
    outlet_name: str
    location: Optional[str] = None
    status: Optional[str] = None
    total_revenue: Decimal
    total_transactions: int
    health_score: Decimal
    rank: Optional[int] = None
    performance_label: str


class DashboardSummaryDTO(BaseModel):
    total_outlets: int
    active_outlets: int
    underperforming_outlets: int
    total_revenue: Decimal
    total_transactions: int
    average_health_score: Decimal
    top_performing_outlet: Optional[FranchiseComparisonDTO] = None
    lowest_performing_outlet: Optional[FranchiseComparisonDTO] = None
    recent_underperformers: List[FranchiseComparisonDTO]


class UnderperformingOutletDTO(BaseModel):
    outlet_id: int
    outlet_name: str
    location: Optional[str] = None
    franchise_id: int
    franchise_name: Optional[str] = None
    total_revenue: Decimal
    franchise_average_revenue: Decimal
    health_score: Decimal
    reason: str


# ------------------- Inventory Schemas -------------------

class ProductBase(BaseModel):
    product_name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[Decimal] = Decimal("0.00")


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    product_id: int


class InventoryBase(BaseModel):
    outlet_id: int
    product_id: int
    current_stock: Optional[Decimal] = Decimal("0.00")
    reorder_point: Optional[Decimal] = Decimal("0.00")
    reorder_quantity: Optional[Decimal] = Decimal("0.00")
    max_stock: Optional[Decimal] = None
    last_updated: Optional[date] = None


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    current_stock: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    max_stock: Optional[Decimal] = None
    last_updated: Optional[date] = None


class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)
    inventory_id: int
    product: Optional[ProductResponse] = None
    outlet: Optional[OutletResponse] = None


class InventoryTransactionBase(BaseModel):
    inventory_id: int
    transaction_date: date
    transaction_type: str  # IN, OUT, WASTAGE, RETURN
    quantity: Optional[Decimal] = Decimal("0.00")
    reason: Optional[str] = None


class InventoryTransactionCreate(InventoryTransactionBase):
    pass


class InventoryTransactionResponse(InventoryTransactionBase):
    model_config = ConfigDict(from_attributes=True)
    transaction_id: int


class PurchaseOrderBase(BaseModel):
    outlet_id: int
    product_id: int
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    quantity: Optional[Decimal] = Decimal("0.00")
    status: Optional[str] = "PENDING"


class PurchaseOrderCreate(PurchaseOrderBase):
    pass


class PurchaseOrderResponse(PurchaseOrderBase):
    model_config = ConfigDict(from_attributes=True)
    order_id: int


class InventoryStatusDTO(BaseModel):
    inventory_id: int
    outlet_id: int
    outlet_name: Optional[str] = None
    product_id: int
    product_name: Optional[str] = None
    category: Optional[str] = None
    current_stock: Decimal
    reorder_point: Decimal
    reorder_quantity: Decimal
    max_stock: Optional[Decimal] = None
    status: str  # Critical, Low Stock, Overstock, Normal


class DemandForecastDTO(BaseModel):
    outlet_id: int
    outlet_name: Optional[str] = None
    product_id: int
    product_name: Optional[str] = None
    forecasted_daily_demand: Decimal
    forecast_period_days: int
    total_historical_demand: Decimal


class StockAlertDTO(BaseModel):
    alert_type: str  # LOW_STOCK, CRITICAL, OVERSTOCK
    outlet_id: int
    outlet_name: Optional[str] = None
    product_id: int
    product_name: Optional[str] = None
    current_stock: Decimal
    threshold: Decimal
    message: str


class ReplenishmentRecommendationDTO(BaseModel):
    outlet_id: int
    outlet_name: Optional[str] = None
    product_id: int
    product_name: Optional[str] = None
    current_stock: Decimal
    forecasted_daily_demand: Decimal
    days_until_stockout: Optional[int] = None
    recommended_order_quantity: Decimal
    recommended_order_date: Optional[date] = None
    reason: str


class InventoryDashboardDTO(BaseModel):
    total_products: int
    total_inventory_items: int
    total_stock_value: Decimal
    low_stock_count: int
    critical_stock_count: int
    overstock_count: int
    total_wastage_30_days: Decimal
    top_alerts: List[StockAlertDTO]
    replenishment_recommendations: List[ReplenishmentRecommendationDTO]
