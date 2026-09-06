"""
Centralised thresholds, weights and constants.

No magic numbers are allowed inline in the core modules — every tuned value
lives here so the FastAPI teammate can review/override without touching logic.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Scoring weights — must sum to 1.0. Preserved exactly from 02_kpi_engine.py
# ---------------------------------------------------------------------------
PERFORMANCE_WEIGHTS: dict[str, float] = {
    "avg_daily_revenue": 0.35,
    "revenue_growth_pct": 0.15,
    "wastage_rate": 0.15,        # lower_is_better
    "absenteeism_rate": 0.15,    # lower_is_better
    "compliance_score": 0.10,
    "campaign_roi": 0.10,
}

# ---------------------------------------------------------------------------
# Health classification cut-offs (0-100 scale)
# ---------------------------------------------------------------------------
HEALTH_THRESHOLDS: dict[str, float] = {
    "healthy": 70.0,   # >= 70  -> Healthy
    "at_risk": 50.0,   # >= 50  -> At Risk,  <50 -> Critical
}

# ---------------------------------------------------------------------------
# Root-cause rule thresholds — preserved from 04_root_cause_engine.py
# ---------------------------------------------------------------------------
ROOT_CAUSE_THRESHOLDS: dict[str, float] = {
    "wastage_rate": 3.0,              # %  -> Inventory Agent
    "peak_understaffed_pct": 15.0,    # %  -> Staff Agent
    "absenteeism_rate": 10.0,         # %  -> Staff Agent
    "compliance_score": 75.0,         # 0-100, below triggers Audit Agent
    "revenue_growth_pct": 0.0,        # %  below 0 -> Outlet Agent warning
    "revenue_drop_pct": -10.0,        # %  severe drop
    "campaign_roi": 0.0,              # %  below 0 -> Marketing Agent
    "stockout_risk_days": 3.0,        # days of cover
}

# Severity ranking (higher = more urgent)
SEVERITY_WEIGHTS: dict[str, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

# ---------------------------------------------------------------------------
# Cleaning / imputation constants
# ---------------------------------------------------------------------------
ROLLING_MEDIAN_WINDOW: int = 7
ROLLING_MEDIAN_CENTER: bool = True
ROLLING_MEDIAN_MIN_PERIODS: int = 1

# ---------------------------------------------------------------------------
# ML hyper-parameters — preserved from 03_ml_forecasting.py
# ---------------------------------------------------------------------------
FORECAST_MODEL_PARAMS: dict[str, object] = {
    "n_estimators": 200,
    "max_depth": 4,
    "learning_rate": 0.08,
    "subsample": 0.9,
    "colsample_bytree": 0.9,
    "random_state": 42,
    "objective": "reg:squarederror",
    "verbosity": 0,
}

RISK_MODEL_PARAMS: dict[str, object] = {
    "n_estimators": 100,
    "max_depth": 3,
    "learning_rate": 0.1,
    "random_state": 42,
    "use_label_encoder": False,
    "eval_metric": "logloss",
    "verbosity": 0,
}

FORECAST_HORIZON_DAYS: int = 7
FORECAST_LAGS: list[int] = [1, 7, 14]
FORECAST_ROLLING_WINDOWS: list[int] = [7, 14]

# Normalisation clip bounds (avoid division by zero when series is constant)
NORM_EPSILON: float = 1e-9
