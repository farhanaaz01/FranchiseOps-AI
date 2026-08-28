"""
Data models for the Outlet Performance Agent
"""
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, date
from pydantic import BaseModel, Field, validator


class Outlet(BaseModel):
    """Outlet information model"""
    outlet_id: str
    outlet_name: str
    location: str
    city: Optional[str] = None
    region: Optional[str] = None
    outlet_type: Optional[str] = None
    opening_date: Optional[date] = None
    status: Literal["active", "inactive", "closed"] = "active"
    operating_hours: Optional[float] = None
    
    class Config:
        arbitrary_types_allowed = True


class SalesRecord(BaseModel):
    """Daily sales record"""
    date: date
    outlet_id: str
    revenue: Optional[float] = None
    transaction_count: Optional[int] = None
    sales_count: Optional[int] = None
    average_order_value: Optional[float] = None
    customer_count: Optional[int] = None
    
    @validator('revenue', pre=True, always=True)
    def validate_revenue(cls, v):
        if v is not None and v < 0:
            raise ValueError("Revenue cannot be negative")
        return v
    
    @validator('transaction_count', pre=True, always=True)
    def validate_transactions(cls, v):
        if v is not None and v < 0:
            raise ValueError("Transaction count cannot be negative")
        return v


class HealthScoreBreakdown(BaseModel):
    """Breakdown of health score components"""
    revenue_performance: float = Field(ge=0, le=100)
    growth: float = Field(ge=0, le=100)
    sales_volume: float = Field(ge=0, le=100)
    trend_consistency: float = Field(ge=0, le=100)
    peer_performance: float = Field(ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "revenue_performance": 75.0,
                "growth": 60.0,
                "sales_volume": 80.0,
                "trend_consistency": 70.0,
                "peer_performance": 65.0
            }
        }


class HealthScore(BaseModel):
    """Outlet health score"""
    outlet_id: str
    score: float = Field(ge=0, le=100)
    category: Literal["EXCELLENT", "GOOD", "STABLE", "AT_RISK", "UNDERPERFORMING", "CRITICAL"]
    breakdown: Optional[HealthScoreBreakdown] = None
    explanation: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "outlet_id": "OUT-101",
                "score": 72.0,
                "category": "GOOD",
                "explanation": "Outlet 101 performed well in revenue but growth is below average"
            }
        }


class OutletPerformance(BaseModel):
    """Complete outlet performance analysis"""
    outlet_id: str
    outlet_name: str
    period: str
    total_revenue: Optional[float] = None
    average_revenue: Optional[float] = None
    transaction_count: Optional[int] = None
    average_order_value: Optional[float] = None
    revenue_growth: Optional[float] = None
    trend: Literal["increasing", "decreasing", "stable", "unknown"] = "unknown"
    health_score: Optional[HealthScore] = None
    rank: Optional[int] = None
    peer_comparison: Optional[Dict[str, Any]] = None
    anomalies: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "outlet_id": "OUT-101",
                "outlet_name": "Mumbai Central",
                "period": "2024-01",
                "total_revenue": 150000.0,
                "revenue_growth": 5.2,
                "trend": "increasing"
            }
        }


class UnderperformingOutlet(BaseModel):
    """Underperforming outlet detection result"""
    outlet_id: str
    outlet_name: str
    status: Literal["UNDERPERFORMING", "AT_RISK", "CRITICAL"]
    severity: Literal["low", "medium", "high", "critical"]
    reasons: List[str]
    supporting_metrics: Dict[str, Any]
    trend: str
    confidence: float = Field(ge=0, le=1)
    recommendations: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "outlet_id": "OUT-104",
                "outlet_name": "Pune East",
                "status": "UNDERPERFORMING",
                "severity": "high",
                "reasons": ["Revenue declined 15%", "Transactions decreased 20%"],
                "trend": "decreasing",
                "confidence": 0.85
            }
        }


class ProposedAction(BaseModel):
    """Proposed consequential action requiring approval"""
    action_type: str
    description: str
    reason: str
    estimated_impact: Optional[str] = None
    cost_estimate: Optional[float] = None
    status: Literal["PENDING_APPROVAL", "APPROVED", "REJECTED", "CANCELLED"] = "PENDING_APPROVAL"
    created_at: datetime = Field(default_factory=datetime.now)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "action_type": "INCREASE_PROMOTIONAL_BUDGET",
                "description": "Increase promotional budget by ₹5,000 for Outlet 104",
                "reason": "Revenue decline due to decreased footfall",
                "estimated_impact": "Expected 5-10% revenue increase",
                "cost_estimate": 5000.0,
                "status": "PENDING_APPROVAL"
            }
        }


class AgentResponse(BaseModel):
    """Standard agent response"""
    intent: str
    status: Literal["success", "error", "needs_clarification", "pending_approval"]
    summary: str
    data: Optional[List[Dict[str, Any]]] = None
    insights: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    warnings: Optional[List[str]] = None
    requires_human_approval: bool = False
    proposed_action: Optional[ProposedAction] = None
    clarification_question: Optional[str] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": "outlet_performance",
                "status": "success",
                "summary": "Outlet 104 is underperforming with 15% revenue decline",
                "confidence": 0.89,
                "requires_human_approval": False
            }
        }