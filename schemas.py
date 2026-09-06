"""
Pydantic schemas for every input/output of the data_engine package.

These models are deliberately FastAPI-ready: they can be used directly as
``response_model`` without translation.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

HealthStatus = Literal["Healthy", "At Risk", "Critical"]
Severity = Literal["low", "medium", "high", "critical"]
AgentDomain = Literal["Outlet", "Inventory", "Staff", "Marketing", "Audit", "Overall"]


# ---------------------------------------------------------------------------
# KPI / performance
# ---------------------------------------------------------------------------
class OutletKPI(BaseModel):
    """Per-outlet KPI snapshot (one row per outlet)."""

    model_config = ConfigDict(extra="forbid")

    outlet_id: Annotated[str, Field(description="Unique outlet identifier")]
    avg_daily_revenue: Annotated[float, Field(description="Mean daily revenue")]
    revenue_growth_pct: Annotated[float, Field(description="Growth last 30d vs prior 30d, %")]
    wastage_rate: Annotated[float, Field(description="Wastage as % of consumed+wastage")]
    absenteeism_rate: Annotated[float, Field(description="Absent days / scheduled days, %")]
    peak_understaffed_pct: Annotated[float, Field(description="Peak-hour understaffed shifts, %")]
    compliance_score: Annotated[float, Field(description="Audit compliance 0-100")]
    campaign_roi: Annotated[float, Field(description="Campaign ROI, %")]
    stockout_risk_flag: Annotated[bool, Field(description="True if days-of-cover below threshold")] = False


class PerformanceScore(BaseModel):
    """Composite 0-100 score and health classification."""

    model_config = ConfigDict(extra="forbid")

    outlet_id: str
    performance_score: Annotated[float, Field(ge=0, le=100, description="Weighted 0-100 score")]
    health_status: HealthStatus
    # optional: normalized components for auditability
    components: dict[str, float] | None = None


# ---------------------------------------------------------------------------
# ML outputs
# ---------------------------------------------------------------------------
class ForecastPoint(BaseModel):
    """Single forecast day for one outlet."""

    model_config = ConfigDict(extra="forbid")

    outlet_id: str
    forecast_date: date
    predicted_revenue: float
    model_version: str = "xgb-v1"


class ForecastResult(BaseModel):
    """7-day forecast for one outlet."""

    model_config = ConfigDict(extra="forbid")

    outlet_id: str
    forecasts: list[ForecastPoint]
    trained_on_rows: int | None = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class RiskFeatureImportance(BaseModel):
    """Feature importance from the risk classifier."""

    model_config = ConfigDict(extra="forbid")

    feature: str
    importance: float


class RiskPrediction(BaseModel):
    """Underperformance risk for one outlet."""

    model_config = ConfigDict(extra="forbid")

    outlet_id: str
    risk_probability: Annotated[float, Field(ge=0, le=1)]
    predicted_label: Literal["Healthy", "At Risk"]
    top_drivers: list[RiskFeatureImportance]


# ---------------------------------------------------------------------------
# Root-cause engine
# ---------------------------------------------------------------------------
class RootCauseIssue(BaseModel):
    """Single structured finding."""

    model_config = ConfigDict(extra="forbid")

    domain: AgentDomain
    severity: Severity
    metric: str
    value: float | None = None
    threshold: float | None = None
    finding: str
    recommendation: str


class RootCauseFinding(BaseModel):
    """Per-outlet root-cause result (JSON handed to LLM layer)."""

    model_config = ConfigDict(extra="forbid")

    outlet_id: str
    performance_score: float
    health_status: HealthStatus
    issues: list[RootCauseIssue]
    priority_issue: str | None = None
    overall_recommendation: str


# ---------------------------------------------------------------------------
# Pipeline envelope (single entry-point output)
# ---------------------------------------------------------------------------
class PipelineOutput(BaseModel):
    """What ``run_outlet_intelligence_pipeline`` returns."""

    model_config = ConfigDict(extra="forbid")

    generated_at: datetime = Field(default_factory=datetime.utcnow)
    outlet_count: int
    kpis: list[OutletKPI]
    performance_scores: list[PerformanceScore]
    forecasts: list[ForecastResult]
    risk_predictions: list[RiskPrediction]
    feature_importances: list[RiskFeatureImportance]
    root_causes: list[RootCauseFinding]

    def to_json_dict(self) -> dict:
        """Return JSON-serialisable dict (dates as ISO strings)."""
        return self.model_dump(mode="json")
