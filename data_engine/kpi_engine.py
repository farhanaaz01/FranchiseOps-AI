"""
KPI calculation + composite outlet performance score (0-100).

Weights and thresholds are imported from :mod:`data_engine.config`,
logic preserved from ``02_kpi_engine.py``. All functions are pure:
DataFrame in, DataFrame out.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from data_engine.config import HEALTH_THRESHOLDS, NORM_EPSILON, PERFORMANCE_WEIGHTS, ROOT_CAUSE_THRESHOLDS


# ---------------------------------------------------------------------------
# normalisation helper
# ---------------------------------------------------------------------------
def normalize_series(series: pd.Series, lower_is_better: bool = False) -> pd.Series:
    """Min-max normalise a series to [0, 1].

    If the series is constant (max-min < epsilon) the function returns 0.5
    for every row to avoid division by zero and to keep the blend neutral.

    Args:
        series: Numeric series to normalise.
        lower_is_better: If True, invert the scale (small values -> 1).

    Returns:
        Series of floats in [0, 1] with the same index.
    """
    s = pd.to_numeric(series, errors="coerce")
    min_v = s.min()
    max_v = s.max()
    if pd.isna(min_v) or pd.isna(max_v) or (max_v - min_v) < NORM_EPSILON:
        return pd.Series(0.5, index=s.index, dtype=float)
    norm = (s - min_v) / (max_v - min_v)
    if lower_is_better:
        norm = 1.0 - norm
    return norm.clip(0, 1)


def classify_health(score: float) -> str:
    """Classify a 0-100 performance score.

    Args:
        score: Composite score 0-100.

    Returns:
        One of ``"Healthy"``, ``"At Risk"``, ``"Critical"``.
    """
    if score >= HEALTH_THRESHOLDS["healthy"]:
        return "Healthy"
    if score >= HEALTH_THRESHOLDS["at_risk"]:
        return "At Risk"
    return "Critical"


# ---------------------------------------------------------------------------
# per-domain KPI helpers (internal)
# ---------------------------------------------------------------------------
def _sales_kpis(sales: pd.DataFrame) -> pd.DataFrame:
    """Compute revenue KPIs per outlet.

    Args:
        sales: Cleaned sales DataFrame with ``outlet_id``, ``date``, ``revenue``.

    Returns:
        DataFrame with ``outlet_id``, ``avg_daily_revenue``, ``revenue_growth_pct``.
    """
    if sales.empty or "outlet_id" not in sales.columns:
        return pd.DataFrame(columns=["outlet_id", "avg_daily_revenue", "revenue_growth_pct"])
    g = sales.groupby("outlet_id")
    avg_rev = g["revenue"].mean().rename("avg_daily_revenue")

    # Growth: last 30 days mean vs prior 30 days mean
    def _growth(group: pd.DataFrame) -> float:
        if "date" not in group.columns or len(group) < 14:
            return 0.0
        grp = group.sort_values("date")
        # Split by median date to get two halves if less than 60 days
        mid = grp["date"].median() if "date" in grp.columns else None
        if grp["date"].nunique() >= 60:
            last30 = grp.tail(30)["revenue"].mean()
            prior30 = grp.tail(60).head(30)["revenue"].mean()
        elif mid is not None:
            last = grp[grp["date"] >= mid]["revenue"].mean()
            prior = grp[grp["date"] < mid]["revenue"].mean()
            last30, prior30 = last, prior
        else:
            return 0.0
        if pd.isna(prior30) or abs(prior30) < NORM_EPSILON:
            return 0.0
        return float((last30 - prior30) / abs(prior30) * 100)

    growth = sales.groupby("outlet_id", group_keys=False).apply(_growth, include_groups=False)
    # pandas apply on groupby returns Series with outlet_id index
    if isinstance(growth, pd.Series):
        growth = growth.rename("revenue_growth_pct")
    else:
        growth = pd.Series(growth, name="revenue_growth_pct")

    out = pd.concat([avg_rev, growth], axis=1).reset_index()
    # Ensure outlet_id column exists
    if "index" in out.columns and "outlet_id" not in out.columns:
        out = out.rename(columns={"index": "outlet_id"})
    return out


def _inventory_kpis(inventory: pd.DataFrame) -> pd.DataFrame:
    """Compute wastage rate per outlet.

    Wastage rate = wastage_qty / (consumed_qty + wastage_qty) * 100.

    Args:
        inventory: Cleaned inventory DataFrame.

    Returns:
        DataFrame with ``outlet_id`` and ``wastage_rate``.
    """
    if inventory.empty or "outlet_id" not in inventory.columns:
        return pd.DataFrame(columns=["outlet_id", "wastage_rate", "stockout_risk_flag"])
    g = inventory.groupby("outlet_id")
    wastage = g["wastage_qty"].sum()
    consumed = g["consumed_qty"].sum()
    denom = consumed + wastage
    rate = (wastage / denom.replace(0, np.nan) * 100).fillna(0).rename("wastage_rate")
    # Stockout risk: avg closing_stock < threshold days of avg consumed
    avg_closing = g["closing_stock"].mean()
    avg_consumed = g["consumed_qty"].mean().replace(0, np.nan)
    days_cover = (avg_closing / avg_consumed).fillna(99)
    flag = (days_cover < ROOT_CAUSE_THRESHOLDS["stockout_risk_days"]).rename("stockout_risk_flag")
    out = pd.concat([rate, flag], axis=1).reset_index()
    if "index" in out.columns and "outlet_id" not in out.columns:
        out = out.rename(columns={"index": "outlet_id"})
    return out


def _staff_kpis(staff: pd.DataFrame) -> pd.DataFrame:
    """Compute absenteeism and peak-understaffed %.

    Args:
        staff: Cleaned staff DataFrame.

    Returns:
        DataFrame with ``outlet_id``, ``absenteeism_rate``, ``peak_understaffed_pct``.
    """
    if staff.empty or "outlet_id" not in staff.columns:
        return pd.DataFrame(columns=["outlet_id", "absenteeism_rate", "peak_understaffed_pct"])
    g = staff.groupby("outlet_id")
    scheduled = g["scheduled"].sum()
    absent = g["absent"].sum() if "absent" in staff.columns else pd.Series(0, index=scheduled.index)
    abs_rate = (absent / scheduled.replace(0, np.nan) * 100).fillna(0).rename("absenteeism_rate")
    if "is_peak_understaffed" in staff.columns:
        peak = staff.groupby("outlet_id")["is_peak_understaffed"].mean() * 100
        peak = peak.rename("peak_understaffed_pct")
    else:
        peak = pd.Series(0, index=scheduled.index, name="peak_understaffed_pct")
    out = pd.concat([abs_rate, peak], axis=1).reset_index()
    if "index" in out.columns and "outlet_id" not in out.columns:
        out = out.rename(columns={"index": "outlet_id"})
    return out


def _audit_kpis(audit: pd.DataFrame) -> pd.DataFrame:
    """Mean compliance score per outlet.

    Args:
        audit: Cleaned audit DataFrame.

    Returns:
        DataFrame with ``outlet_id`` and ``compliance_score``.
    """
    if audit.empty or "outlet_id" not in audit.columns:
        return pd.DataFrame(columns=["outlet_id", "compliance_score"])
    if "compliance_score" not in audit.columns:
        # Default if column missing
        outlets = audit["outlet_id"].unique()
        return pd.DataFrame({"outlet_id": outlets, "compliance_score": 75.0})
    out = audit.groupby("outlet_id")["compliance_score"].mean().rename("compliance_score").reset_index()
    if "index" in out.columns and "outlet_id" not in out.columns:
        out = out.rename(columns={"index": "outlet_id"})
    return out


def _marketing_kpis(marketing: pd.DataFrame) -> pd.DataFrame:
    """Mean campaign ROI per outlet.

    Args:
        marketing: Cleaned marketing DataFrame.

    Returns:
        DataFrame with ``outlet_id`` and ``campaign_roi``.
    """
    if marketing.empty or "outlet_id" not in marketing.columns:
        return pd.DataFrame(columns=["outlet_id", "campaign_roi"])
    col = "roi" if "roi" in marketing.columns else ("campaign_roi" if "campaign_roi" in marketing.columns else None)
    if col is None:
        outlets = marketing["outlet_id"].unique()
        return pd.DataFrame({"outlet_id": outlets, "campaign_roi": 0.0})
    out = marketing.groupby("outlet_id")[col].mean().rename("campaign_roi").reset_index()
    if "index" in out.columns and "outlet_id" not in out.columns:
        out = out.rename(columns={"index": "outlet_id"})
    return out


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------
def compute_outlet_kpis(
    sales: pd.DataFrame,
    inventory: pd.DataFrame,
    staff: pd.DataFrame,
    marketing: pd.DataFrame,
    audit: pd.DataFrame,
) -> pd.DataFrame:
    """Compute the full KPI table — one row per outlet.

    Merges per-domain KPIs with outer joins so an outlet appearing in any
    table is included. Missing KPIs are filled with neutral defaults.

    Args:
        sales: Cleaned sales DataFrame.
        inventory: Cleaned inventory DataFrame.
        staff: Cleaned staff DataFrame.
        marketing: Cleaned marketing DataFrame.
        audit: Cleaned audit DataFrame.

    Returns:
        DataFrame with columns ``outlet_id``, ``avg_daily_revenue``,
        ``revenue_growth_pct``, ``wastage_rate``, ``absenteeism_rate``,
        ``peak_understaffed_pct``, ``compliance_score``, ``campaign_roi``,
        ``stockout_risk_flag``.

    Raises:
        ValueError: If all five inputs are empty.
    """
    parts = [
        _sales_kpis(sales),
        _inventory_kpis(inventory),
        _staff_kpis(staff),
        _audit_kpis(audit),
        _marketing_kpis(marketing),
    ]
    # Collect all outlet_ids
    all_outlets = set()
    for p in parts:
        if not p.empty and "outlet_id" in p.columns:
            all_outlets.update(p["outlet_id"].tolist())
    if not all_outlets:
        # No outlets at all — try to extract from raw sales/inventory even if KPI calc failed
        for df in [sales, inventory, staff, marketing, audit]:
            if not df.empty and "outlet_id" in df.columns:
                all_outlets.update(df["outlet_id"].unique().tolist())
        if not all_outlets:
            raise ValueError("No outlets found in any input table.")

    base = pd.DataFrame({"outlet_id": sorted(all_outlets)})
    kpi = base
    for p in parts:
        if not p.empty:
            kpi = kpi.merge(p, on="outlet_id", how="left")

    # Fill missing with neutral defaults
    defaults: dict[str, float | bool] = {
        "avg_daily_revenue": 0.0,
        "revenue_growth_pct": 0.0,
        "wastage_rate": 0.0,
        "absenteeism_rate": 0.0,
        "peak_understaffed_pct": 0.0,
        "compliance_score": 75.0,
        "campaign_roi": 0.0,
        "stockout_risk_flag": False,
    }
    for col, default in defaults.items():
        if col not in kpi.columns:
            kpi[col] = default
        else:
            kpi[col] = kpi[col].fillna(default)

    return kpi


def calculate_performance_scores(kpi_df: pd.DataFrame) -> pd.DataFrame:
    """Blend KPIs into a composite 0-100 score and health status.

    Formula preserved from the spec::
        score = 0.35*norm(avg_daily_revenue)
              + 0.15*norm(growth_pct)
              + 0.15*norm(wastage_rate, lower_is_better=True)
              + 0.15*norm(absenteeism, lower_is_better=True)
              + 0.10*norm(compliance_score)
              + 0.10*norm(campaign_roi)
        performance_score = round(score*100, 1)

    Normalisation is min-max across the batch (all outlets). This matches
    the original Python logic which normalised across the outlet cohort.

    Args:
        kpi_df: Output of :func:`compute_outlet_kpis`.

    Returns:
        DataFrame with ``outlet_id``, ``performance_score`` (0-100, 1 decimal),
        ``health_status`` and per-component normalised values (for auditability).

    Raises:
        ValueError: If ``kpi_df`` is empty or missing required columns.
    """
    if kpi_df.empty:
        raise ValueError("kpi_df is empty — cannot score.")
    required = ["outlet_id", "avg_daily_revenue", "revenue_growth_pct", "wastage_rate", "absenteeism_rate", "compliance_score", "campaign_roi"]
    missing = [c for c in required if c not in kpi_df.columns]
    if missing:
        raise ValueError(f"kpi_df missing columns: {missing}")

    norm_map = {
        "avg_daily_revenue": normalize_series(kpi_df["avg_daily_revenue"], False),
        "revenue_growth_pct": normalize_series(kpi_df["revenue_growth_pct"], False),
        "wastage_rate": normalize_series(kpi_df["wastage_rate"], True),
        "absenteeism_rate": normalize_series(kpi_df["absenteeism_rate"], True),
        "compliance_score": normalize_series(kpi_df["compliance_score"], False),
        "campaign_roi": normalize_series(kpi_df["campaign_roi"], False),
    }

    score_01 = sum(PERFORMANCE_WEIGHTS[k] * norm_map[k] for k in PERFORMANCE_WEIGHTS)
    result = kpi_df[["outlet_id"]].copy()
    result["performance_score"] = (score_01 * 100).round(1)
    result["health_status"] = result["performance_score"].apply(classify_health)
    # Keep normalised components for downstream audit
    for k, v in norm_map.items():
        result[f"norm_{k}"] = v.round(4)

    return result
