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
