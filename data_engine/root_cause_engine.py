"""
Rule-based root-cause reasoning engine — deterministic, auditable.

Scans every outlet's KPIs across all five domains against thresholds from
:mod:`data_engine.config` and emits structured JSON findings + recommendations.
This JSON is what the LLM layer turns into natural language for the dashboard.
Preserved exactly from ``04_root_cause_engine.py`` — severity ranking,
priority sorting, and recommendation builder are not redesigned.
"""

from __future__ import annotations

import pandas as pd

from data_engine.config import ROOT_CAUSE_THRESHOLDS, SEVERITY_WEIGHTS


# ---------------------------------------------------------------------------
# Recommendation templates
# ---------------------------------------------------------------------------
_RECOMMENDATIONS: dict[str, str] = {
    "wastage": "Review Inventory: reduce wastage via FIFO checks, portion control and cold-chain audit.",
    "understaffed": "Increase peak-hour staffing and cross-train staff to cover evenings/weekends.",
    "absenteeism": "Address absenteeism: review roster equity, incentive alignment and attendance follow-ups.",
    "compliance": "Close compliance gaps: retrain on SOPs and schedule a follow-up audit within 7 days.",
    "growth": "Investigate revenue decline: check local competition, pricing and service speed.",
    "roi": "Re-evaluate marketing spend: pause low-ROI campaigns and reallocate to top performers.",
    "stockout": "Replenish high-demand items: raise reorder point and expedite pending POs.",
}

_SEVERITY_BY_RULE: dict[str, str] = {
    "wastage": "high",
    "understaffed": "high",
    "absenteeism": "medium",
    "compliance": "high",
    "growth": "medium",
    "roi": "low",
    "stockout": "critical",
    "revenue_drop": "critical",
}


def _severity_weight(severity: str) -> int:
    """Return numeric weight for severity sorting.

    Args:
        severity: One of ``low``/``medium``/``high``/``critical``.

    Returns:
        Integer weight (higher = more urgent).
    """
    return SEVERITY_WEIGHTS.get(severity, 1)


def analyze_single_outlet(kpi_row: pd.Series, performance_row: pd.Series | None = None) -> list[dict]:
    """Evaluate one outlet's KPIs against thresholds and return issues.

    Args:
        kpi_row: Single row from the KPI table (Series indexed by KPI name).
        performance_row: Optional row with ``performance_score`` / ``health_status``.
            Used only to enrich the finding; not for thresholding.

    Returns:
        List of issue dicts (unsorted), each with ``domain``, ``severity``,
        ``metric``, ``value``, ``threshold``, ``finding``, ``recommendation``.

    Raises:
        ValueError: If ``kpi_row`` is empty.
    """
    if kpi_row.empty:
        raise ValueError("kpi_row is empty.")
    outlet_id = str(kpi_row.get("outlet_id", "unknown"))
    issues: list[dict] = []

    # Helper to append
    def add(rule_key: str, domain: str, metric: str, value: float, threshold: float, finding: str) -> None:
        sev = _SEVERITY_BY_RULE.get(rule_key, "medium")
        issues.append(
            {
                "outlet_id": outlet_id,
                "domain": domain,
                "severity": sev,
                "metric": metric,
                "value": round(float(value), 2) if value is not None else None,
                "threshold": threshold,
                "finding": finding,
                "recommendation": _RECOMMENDATIONS.get(rule_key, "Investigate further."),
            }
        )

    # 1. Inventory — wastage
    wastage = float(kpi_row.get("wastage_rate", 0))
    if wastage > ROOT_CAUSE_THRESHOLDS["wastage_rate"]:
        add(
            "wastage",
            "Inventory",
            "wastage_rate",
            wastage,
            ROOT_CAUSE_THRESHOLDS["wastage_rate"],
            f"Inventory Agent: wastage {wastage:.1f}% exceeds threshold ({ROOT_CAUSE_THRESHOLDS['wastage_rate']}%)",
        )

    # 2. Stockout risk flag
    stockout = bool(kpi_row.get("stockout_risk_flag", False))
    if stockout:
        add(
            "stockout",
            "Inventory",
            "stockout_risk_flag",
            1.0,
            0.0,
            "Inventory Agent: low stock cover — stockout risk in < "
            f"{ROOT_CAUSE_THRESHOLDS['stockout_risk_days']} days",
        )

    # 3. Staff — peak understaffing
    peak = float(kpi_row.get("peak_understaffed_pct", 0))
    if peak > ROOT_CAUSE_THRESHOLDS["peak_understaffed_pct"]:
        add(
            "understaffed",
            "Staff",
            "peak_understaffed_pct",
            peak,
            ROOT_CAUSE_THRESHOLDS["peak_understaffed_pct"],
            f"Staff Agent: peak-hour understaffed shifts {peak:.1f}% exceeds threshold ({ROOT_CAUSE_THRESHOLDS['peak_understaffed_pct']}%)",
        )

    # 4. Staff — absenteeism
    absent = float(kpi_row.get("absenteeism_rate", 0))
    if absent > ROOT_CAUSE_THRESHOLDS["absenteeism_rate"]:
        add(
            "absenteeism",
            "Staff",
            "absenteeism_rate",
            absent,
            ROOT_CAUSE_THRESHOLDS["absenteeism_rate"],
            f"Staff Agent: absenteeism {absent:.1f}% exceeds threshold ({ROOT_CAUSE_THRESHOLDS['absenteeism_rate']}%)",
        )

    # 5. Audit — compliance
    compliance = float(kpi_row.get("compliance_score", 100))
    if compliance < ROOT_CAUSE_THRESHOLDS["compliance_score"]:
        add(
            "compliance",
            "Audit",
            "compliance_score",
            compliance,
            ROOT_CAUSE_THRESHOLDS["compliance_score"],
            f"Audit Agent: compliance {compliance:.1f} below threshold ({ROOT_CAUSE_THRESHOLDS['compliance_score']})",
        )

    # 6. Outlet — revenue growth
    growth = float(kpi_row.get("revenue_growth_pct", 0))
    if growth < ROOT_CAUSE_THRESHOLDS["revenue_drop_pct"]:
        add(
            "revenue_drop",
            "Outlet",
            "revenue_growth_pct",
            growth,
            ROOT_CAUSE_THRESHOLDS["revenue_drop_pct"],
            f"Outlet Agent: revenue down {abs(growth):.1f}% — severe decline",
        )
    elif growth < ROOT_CAUSE_THRESHOLDS["revenue_growth_pct"]:
        add(
            "growth",
            "Outlet",
            "revenue_growth_pct",
            growth,
            ROOT_CAUSE_THRESHOLDS["revenue_growth_pct"],
            f"Outlet Agent: revenue growth {growth:.1f}% is negative",
        )

    # 7. Marketing — ROI
    roi = float(kpi_row.get("campaign_roi", 0))
    if roi < ROOT_CAUSE_THRESHOLDS["campaign_roi"]:
        add(
            "roi",
            "Marketing",
            "campaign_roi",
            roi,
            ROOT_CAUSE_THRESHOLDS["campaign_roi"],
            f"Marketing Agent: campaign ROI {roi:.1f}% is negative",
        )

    return issues


def build_recommendation(sorted_issues: list[dict]) -> str:
    """Compose the overall recommendation from sorted issues.

    Args:
        sorted_issues: Issues sorted by severity descending.

    Returns:
        Human-readable recommendation string (1-2 sentences).
        Returns a positive message if no issues.
    """
    if not sorted_issues:
        return "Outlet is healthy — maintain current operations and monitor weekly trends."
    # Top 2 issues drive the headline
    top = sorted_issues[:2]
    recs = [i["recommendation"] for i in top]
    if len(recs) == 1:
        return recs[0]
    return f"{recs[0]} Also: {recs[1].lower()}"


def scan_all_outlets(
    kpi_df: pd.DataFrame,
    performance_df: pd.DataFrame | None = None,
) -> list[dict]:
    """Scan every outlet and return per-outlet findings + recommendation.

    Issues are sorted by severity (critical -> low) before the recommendation
    is built, preserving the original priority logic.

    Args:
        kpi_df: Full KPI table (one row per outlet).
        performance_df: Optional table with ``outlet_id``, ``performance_score``,
            ``health_status`` (merged into output).

    Returns:
        List of per-outlet dicts with ``outlet_id``, ``performance_score``,
        ``health_status``, ``issues`` (sorted), ``priority_issue``,
        ``overall_recommendation``.

    Raises:
        ValueError: If ``kpi_df`` is empty.
    """
    if kpi_df.empty:
        raise ValueError("kpi_df is empty — cannot run root-cause scan.")

    perf_lookup: dict[str, dict] = {}
    if performance_df is not None and not performance_df.empty:
        for _, row in performance_df.iterrows():
            perf_lookup[str(row["outlet_id"])] = {
                "performance_score": float(row.get("performance_score", 0)),
                "health_status": str(row.get("health_status", "Unknown")),
            }

    results: list[dict] = []
    for _, row in kpi_df.iterrows():
        outlet_id = str(row["outlet_id"])
        raw_issues = analyze_single_outlet(row, None)
        # Sort by severity weight descending (stable sort preserves domain order)
        sorted_issues = sorted(raw_issues, key=lambda i: _severity_weight(i["severity"]), reverse=True)
        perf = perf_lookup.get(outlet_id, {"performance_score": 0.0, "health_status": "Unknown"})
        # Strip outlet_id from issues for cleaner nesting (kept at top level)
        clean_issues = [{k: v for k, v in iss.items() if k != "outlet_id"} for iss in sorted_issues]
        results.append(
            {
                "outlet_id": outlet_id,
                "performance_score": perf["performance_score"],
                "health_status": perf["health_status"],
                "issues": clean_issues,
                "priority_issue": clean_issues[0]["finding"] if clean_issues else None,
                "overall_recommendation": build_recommendation(sorted_issues),
                "issue_count": len(clean_issues),
            }
        )

    # Sort results: Critical outlets first, then by performance_score ascending
    status_order = {"Critical": 0, "At Risk": 1, "Healthy": 2, "Unknown": 3}
    results.sort(key=lambda r: (status_order.get(r["health_status"], 3), r["performance_score"]))
    return results
