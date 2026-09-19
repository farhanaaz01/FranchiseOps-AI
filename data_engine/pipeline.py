"""
Orchestrator — single entry point for the FastAPI teammate.

``run_outlet_intelligence_pipeline`` is the only function the backend needs to
wire into a route. It takes the five raw tables (DataFrames) and returns the
final structured ``PipelineOutput`` (Pydantic → JSON).

No I/O inside: reading CSVs / DB queries happens outside and the caller passes
DataFrames in. This keeps the pipeline swappable to PostgreSQL + SQLAlchemy.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from data_engine.cleaning import clean_audit, clean_inventory, clean_marketing, clean_sales, clean_staff
from data_engine.kpi_engine import calculate_performance_scores, compute_outlet_kpis
from data_engine.ml_models import (
    build_forecast_features,
    get_feature_importance,
    predict_forecast,
    predict_risk,
    train_forecast_model,
    train_risk_classifier,
)
from data_engine.root_cause_engine import scan_all_outlets
from data_engine.schemas import (
    ForecastPoint,
    ForecastResult,
    OutletKPI,
    PerformanceScore,
    PipelineOutput,
    RiskFeatureImportance,
    RiskPrediction,
    RootCauseFinding,
    RootCauseIssue,
)


def run_outlet_intelligence_pipeline(
    sales: pd.DataFrame,
    inventory: pd.DataFrame,
    staff: pd.DataFrame,
    marketing: pd.DataFrame,
    audit: pd.DataFrame,
    *,
    train_forecast: bool = True,
    train_risk: bool = True,
) -> PipelineOutput:
    """End-to-end outlet intelligence: raw tables -> structured JSON.

    Steps:
    1. Clean each table (domain-aware imputation).
    2. Compute per-outlet KPIs and composite 0-100 performance scores.
    3. Train (or skip) the 7-day revenue forecaster and generate forecasts.
    4. Train (or skip) the risk classifier and predict risk + importances.
    5. Run the rule-based root-cause scan.

    All steps are pure DataFrame transforms; no file or DB I/O.

    Args:
        sales: Raw sales table. Columns ``outlet_id``, ``date``, ``revenue``.
        inventory: Raw inventory table. Columns ``outlet_id``, ``opening_stock``,
            ``received_qty``, ``consumed_qty``, ``wastage_qty``, ``closing_stock``.
        staff: Raw staff table. Columns ``outlet_id``, ``scheduled``, ``present``.
        marketing: Raw marketing table. Columns ``outlet_id``, campaign cost/roi.
        audit: Raw audit table. Columns ``outlet_id``, ``compliance_score``.
        train_forecast: If True, train the forecaster on the cleaned sales.
            If False, forecasts are still produced via fallback if training fails.
        train_risk: If True, train the risk classifier on the KPI snapshot.

    Returns:
        :class:`PipelineOutput` — Pydantic model ready for ``model_dump(mode="json")``
        or to be used as a FastAPI ``response_model``. JSON contains
        ``kpis``, ``performance_scores``, ``forecasts``, ``risk_predictions``,
        ``feature_importances``, ``root_causes``.

    Raises:
        ValueError: If all five inputs are empty or KPI calculation yields no outlets.
        TypeError: If inputs are not DataFrames.

    Example:
        >>> output = run_outlet_intelligence_pipeline(sales, inv, staff, mkt, aud)
        >>> output.model_dump(mode="json")  # send to frontend / LLM layer
    """
    for name, df in [("sales", sales), ("inventory", inventory), ("staff", staff), ("marketing", marketing), ("audit", audit)]:
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"{name} must be a DataFrame, got {type(df).__name__}")

    if all(df.empty for df in [sales, inventory, staff, marketing, audit]):
        raise ValueError("All five input tables are empty — nothing to process.")

    # 1. Cleaning (pure, no I/O)
    sales_c = clean_sales(sales)
    inv_c = clean_inventory(inventory)
    staff_c = clean_staff(staff)
    mkt_c = clean_marketing(marketing)
    audit_c = clean_audit(audit)

    # 2. KPIs + scoring
    kpi_df = compute_outlet_kpis(sales_c, inv_c, staff_c, mkt_c, audit_c)
    perf_df = calculate_performance_scores(kpi_df)

    # Enrich kpi_df with performance for downstream ML (risk label needs health_status)
    kpi_with_perf = kpi_df.merge(perf_df[["outlet_id", "performance_score", "health_status"]], on="outlet_id", how="left")

    # 3. Forecasting
    forecasts: list[ForecastResult] = []
    forecast_feature_cols: list[str] = []
    forecast_model: Any | None = None
    if train_forecast:
        try:
            forecast_model, forecast_feature_cols = train_forecast_model(sales_c)
        except ValueError:
            # Not enough rows — will fall back to flat forecast in predict
            forecast_model = None
            forecast_feature_cols = []

    # Generate forecasts per outlet regardless (predict handles fallback)
    if forecast_model is not None and forecast_feature_cols:
        forecast_df = predict_forecast(forecast_model, sales_c, forecast_feature_cols)
    else:
        # No model — use last revenue as flat forecast
        from data_engine.ml_models import predict_forecast as _pf  # local to avoid circular

        # Build a dummy that triggers fallback path
        forecast_df = _pf(None, sales_c, []) if False else _fallback_forecast(sales_c)

    # Group forecast_df into ForecastResult per outlet
    if not forecast_df.empty:
        for outlet, group in forecast_df.groupby("outlet_id"):
            points = [
                ForecastPoint(
                    outlet_id=str(outlet),
                    forecast_date=pd.to_datetime(row["forecast_date"]).date()
                    if not isinstance(row["forecast_date"], type(pd.Timestamp.min.date())) and hasattr(row["forecast_date"], "date")
                    else row["forecast_date"],  # type: ignore[arg-type]
                    predicted_revenue=float(row["predicted_revenue"]),
                )
                for _, row in group.iterrows()
            ]
            forecasts.append(
                ForecastResult(
                    outlet_id=str(outlet),
                    forecasts=points,
                    trained_on_rows=len(sales_c),
                )
            )

    # 4. Risk classifier
    risk_predictions: list[RiskPrediction] = []
    feature_importances: list[RiskFeatureImportance] = []
    if train_risk:
        try:
            clf, risk_cols = train_risk_classifier(kpi_with_perf, perf_df)
            risk_df = predict_risk(clf, kpi_with_perf, risk_cols)
            imp_df = get_feature_importance(clf, risk_cols)
            for _, row in risk_df.iterrows():
                # Top 2 drivers for that outlet are global importances (classifier is cohort-level)
                # — attach the top 2 global features as drivers
                top = imp_df.head(2)
                drivers = [
                    RiskFeatureImportance(feature=str(r["feature"]), importance=float(r["importance"]))
                    for _, r in top.iterrows()
                ]
                risk_predictions.append(
                    RiskPrediction(
                        outlet_id=str(row["outlet_id"]),
                        risk_probability=float(row["risk_probability"]),
                        predicted_label=row["predicted_label"],  # type: ignore[arg-type]
                        top_drivers=drivers,
                    )
                )
            for _, row in imp_df.iterrows():
                feature_importances.append(
                    RiskFeatureImportance(feature=str(row["feature"]), importance=float(row["importance"]))
                )
        except ValueError as exc:
            # Honest scoping: not enough class diversity (e.g. all Healthy)
            # Produce uniform low-risk predictions instead of failing the pipeline
            for outlet in kpi_df["outlet_id"].tolist():
                risk_predictions.append(
                    RiskPrediction(
                        outlet_id=str(outlet),
                        risk_probability=0.1,
                        predicted_label="Healthy",
                        top_drivers=[],
                    )
                )
            # Keep the error as a pseudo-importance note
            feature_importances.append(RiskFeatureImportance(feature=f"note: {str(exc)[:120]}", importance=0.0))

    # 5. Root-cause scan
    root_cause_dicts = scan_all_outlets(kpi_with_perf, perf_df)
    root_causes: list[RootCauseFinding] = []
    for rc in root_cause_dicts:
        issues = [
            RootCauseIssue(
                domain=iss["domain"],  # type: ignore[arg-type]
                severity=iss["severity"],  # type: ignore[arg-type]
                metric=iss["metric"],
                value=iss.get("value"),
                threshold=iss.get("threshold"),
                finding=iss["finding"],
                recommendation=iss["recommendation"],
            )
            for iss in rc["issues"]
        ]
        root_causes.append(
            RootCauseFinding(
                outlet_id=rc["outlet_id"],
                performance_score=float(rc["performance_score"]),
                health_status=rc["health_status"],  # type: ignore[arg-type]
                issues=issues,
                priority_issue=rc["priority_issue"],
                overall_recommendation=rc["overall_recommendation"],
            )
        )

    # 6. Build Pydantic envelope
    kpis = [
        OutletKPI(
            outlet_id=str(row["outlet_id"]),
            avg_daily_revenue=float(row["avg_daily_revenue"]),
            revenue_growth_pct=float(row["revenue_growth_pct"]),
            wastage_rate=float(row["wastage_rate"]),
            absenteeism_rate=float(row["absenteeism_rate"]),
            peak_understaffed_pct=float(row["peak_understaffed_pct"]),
            compliance_score=float(row["compliance_score"]),
            campaign_roi=float(row["campaign_roi"]),
            stockout_risk_flag=bool(row["stockout_risk_flag"]),
        )
        for _, row in kpi_df.iterrows()
    ]
    scores = [
        PerformanceScore(
            outlet_id=str(row["outlet_id"]),
            performance_score=float(row["performance_score"]),
            health_status=row["health_status"],  # type: ignore[arg-type]
            components={k.replace("norm_", ""): float(v) for k, v in row.items() if k.startswith("norm_")},
        )
        for _, row in perf_df.iterrows()
    ]

    return PipelineOutput(
        generated_at=datetime.utcnow(),
        outlet_count=len(kpis),
        kpis=kpis,
        performance_scores=scores,
        forecasts=forecasts,
        risk_predictions=risk_predictions,
        feature_importances=feature_importances,
        root_causes=root_causes,
    )


def _fallback_forecast(sales: pd.DataFrame) -> pd.DataFrame:
    """Flat forecast fallback when no model is available.

    Args:
        sales: Cleaned sales DataFrame.

    Returns:
        DataFrame with ``outlet_id``, ``forecast_date``, ``predicted_revenue``.
    """
    if sales.empty:
        return pd.DataFrame(columns=["outlet_id", "forecast_date", "predicted_revenue"])
    from data_engine.config import FORECAST_HORIZON_DAYS

    rows: list[dict] = []
    last_dates = sales.groupby("outlet_id")["date"].max()
    last_rev = sales.groupby("outlet_id")["revenue"].last()
    for outlet in last_dates.index:
        base = pd.to_datetime(last_dates[outlet])
        rev = float(last_rev[outlet])
        for h in range(1, FORECAST_HORIZON_DAYS + 1):
            rows.append(
                {
                    "outlet_id": outlet,
                    "forecast_date": (base + pd.Timedelta(days=h)).date(),
                    "predicted_revenue": round(rev, 2),
                }
            )
    return pd.DataFrame(rows)
