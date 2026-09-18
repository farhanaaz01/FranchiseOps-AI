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


# ------------------- Milestone 3: Workforce & Marketing Schemas -------------------

class EmployeeBase(BaseModel):
    outlet_id: int
    full_name: str
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    hourly_rate: Optional[Decimal] = Decimal("0.00")
    hire_date: Optional[date] = None
    status: Optional[str] = "Active"


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)
    employee_id: int


class AttendanceBase(BaseModel):
    employee_id: int
    attendance_date: date
    status: str  # PRESENT, ABSENT, LATE, HALF_DAY
    hours_worked: Optional[Decimal] = Decimal("0.00")
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    model_config = ConfigDict(from_attributes=True)
    attendance_id: int


class ScheduleBase(BaseModel):
    employee_id: int
    schedule_date: date
    shift_start: Optional[str] = None
    shift_end: Optional[str] = None
    status: Optional[str] = "SCHEDULED"


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleResponse(ScheduleBase):
    model_config = ConfigDict(from_attributes=True)
    schedule_id: int


class MarketingCampaignBase(BaseModel):
    outlet_id: int
    campaign_name: str
    campaign_type: Optional[str] = None
    start_date: date
    end_date: date
    budget: Optional[Decimal] = Decimal("0.00")
    status: Optional[str] = "Active"


class MarketingCampaignCreate(MarketingCampaignBase):
    pass


class MarketingCampaignResponse(MarketingCampaignBase):
    model_config = ConfigDict(from_attributes=True)
    campaign_id: int


class CampaignPerformanceBase(BaseModel):
    campaign_id: int
    performance_date: date
    impressions: Optional[int] = 0
    clicks: Optional[int] = 0
    conversions: Optional[int] = 0
    engagement_score: Optional[Decimal] = Decimal("0.00")
    revenue: Optional[Decimal] = Decimal("0.00")


class CampaignPerformanceCreate(CampaignPerformanceBase):
    pass


class CampaignPerformanceResponse(CampaignPerformanceBase):
    model_config = ConfigDict(from_attributes=True)
    performance_id: int


class EmployeePerformanceDTO(BaseModel):
    employee_id: int
    full_name: str
    outlet_id: int
    outlet_name: Optional[str] = None
    role: Optional[str] = None
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    half_day_days: int
    attendance_rate: Decimal
    total_hours_worked: Decimal
    average_hours_per_day: Decimal
    productivity_score: Decimal  # 0-100
    performance_label: str


class OutletWorkforceDTO(BaseModel):
    outlet_id: int
    outlet_name: Optional[str] = None
    total_employees: int
    active_employees: int
    average_attendance_rate: Decimal
    total_hours_worked: Decimal
    staffing_shortage_count: int
    employee_performances: List[EmployeePerformanceDTO]


class StaffingAlertDTO(BaseModel):
    outlet_id: int
    outlet_name: Optional[str] = None
    alert_type: str  # SHORTAGE, OVERSTAFFED
    scheduled_staff_count: int
    expected_staff_count: int
    message: str


class WorkforceDashboardDTO(BaseModel):
    total_employees: int
    active_employees: int
    total_outlets_with_employees: int
    average_attendance_rate: Decimal
    total_hours_worked: Decimal
    top_performers: List[EmployeePerformanceDTO]
    underperformers: List[EmployeePerformanceDTO]
    staffing_alerts: List[StaffingAlertDTO]


class CampaignAnalyticsDTO(BaseModel):
    campaign_id: int
    campaign_name: str
    outlet_id: int
    outlet_name: Optional[str] = None
    campaign_type: Optional[str] = None
    start_date: date
    end_date: date
    budget: Decimal
    total_revenue: Decimal
    total_impressions: int
    total_clicks: int
    total_conversions: int
    average_engagement_score: Decimal
    roi_percentage: Decimal
    engagement_rate: Decimal  # clicks / impressions
    conversion_rate: Decimal  # conversions / clicks
    status: str
    performance_label: str


class MarketingDashboardDTO(BaseModel):
    total_campaigns: int
    active_campaigns: int
    total_budget: Decimal
    total_revenue: Decimal
    overall_roi_percentage: Decimal
    average_engagement_rate: Decimal
    average_conversion_rate: Decimal
    top_campaigns: List[CampaignAnalyticsDTO]
    underperforming_campaigns: List[CampaignAnalyticsDTO]
    campaigns_by_type: dict[str, int]
