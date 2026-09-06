"""
pytest unit tests with small synthetic data.

Run:  pytest data_engine/tests -v
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from data_engine.cleaning import clean_inventory, clean_sales
from data_engine.kpi_engine import calculate_performance_scores, compute_outlet_kpis
from data_engine.ml_models import build_forecast_features, load_model, save_model, train_forecast_model
from data_engine.pipeline import run_outlet_intelligence_pipeline


# ---------------------------------------------------------------------------
# fixtures — small synthetic data (3 outlets, 30 days)
# ---------------------------------------------------------------------------
@pytest.fixture
def sales_raw() -> pd.DataFrame:
    rng = pd.date_range("2025-01-01", periods=30, freq="D")
    rows = []
    for outlet in ["OUT-01", "OUT-02", "OUT-03"]:
        base = 5000 if outlet == "OUT-01" else 3000
        for d in rng:
            rev = base + np.random.randint(-500, 500)
            # Inject negatives and NaNs
            if np.random.rand() < 0.05:
                rev = -100
            if np.random.rand() < 0.03:
                rev = np.nan  # type: ignore[assignment]
            rows.append({"outlet_id": outlet, "date": d, "revenue": rev})
    # duplicate a row
    rows.append(rows[0])
    return pd.DataFrame(rows)


@pytest.fixture
def inventory_raw() -> pd.DataFrame:
    rows = []
    for outlet in ["OUT-01", "OUT-02", "OUT-03"]:
        for i in range(10):
            rows.append(
                {
                    "outlet_id": outlet,
                    "opening_stock": 100 + i * 2,
                    "received_qty": 50,
                    "consumed_qty": 40,
                    "wastage_qty": 2 if outlet != "OUT-02" else 10,  # OUT-02 has high wastage
                    "closing_stock": np.nan if i == 5 else 100 + i * 2 + 50 - 40 - 2,
                }
            )
    return pd.DataFrame(rows)


@pytest.fixture
def staff_raw() -> pd.DataFrame:
    rng = pd.date_range("2025-01-01", periods=30, freq="D")
    rows = []
    for outlet in ["OUT-01", "OUT-02", "OUT-03"]:
        for d in rng:
            scheduled = 10
            present = 9 if outlet == "OUT-01" else 6  # OUT-02/03 have absenteeism
            rows.append(
                {
                    "outlet_id": outlet,
                    "date": d,
                    "scheduled": scheduled,
                    "present": present,
                    "is_peak_understaffed": outlet == "OUT-03",
                }
            )
    return pd.DataFrame(rows)


@pytest.fixture
def marketing_raw() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"outlet_id": "OUT-01", "campaign_cost": 5000, "revenue_attributed": 8000, "roi": 60},
            {"outlet_id": "OUT-02", "campaign_cost": 5000, "revenue_attributed": 4000, "roi": -20},
            {"outlet_id": "OUT-03", "campaign_cost": 5000, "revenue_attributed": 5000, "roi": 0},
        ]
    )


@pytest.fixture
def audit_raw() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"outlet_id": "OUT-01", "compliance_score": 90},
            {"outlet_id": "OUT-02", "compliance_score": 60},
            {"outlet_id": "OUT-03", "compliance_score": 75},
        ]
    )


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------
def test_clean_sales_no_negatives(sales_raw: pd.DataFrame) -> None:
    cleaned = clean_sales(sales_raw)
    assert (cleaned["revenue"] < 0).sum() == 0
    assert len(cleaned) < len(sales_raw)  # duplicate removed


def test_clean_sales_empty() -> None:
    empty = pd.DataFrame(columns=["outlet_id", "revenue"])
    result = clean_sales(empty)
    assert result.empty


def test_clean_inventory_flow(sales_raw: pd.DataFrame, inventory_raw: pd.DataFrame) -> None:
    cleaned = clean_inventory(inventory_raw)
    # previously NaN closing_stock should be reconstructed
    assert cleaned["closing_stock"].isna().sum() == 0
    # check flow for a row where closing was NaN
    assert cleaned["closing_stock"].min() >= 0


def test_kpi_and_scoring(staff_raw: pd.DataFrame, inventory_raw: pd.DataFrame, marketing_raw: pd.DataFrame, audit_raw: pd.DataFrame, sales_raw: pd.DataFrame) -> None:
    from data_engine.cleaning import clean_audit, clean_inventory, clean_marketing, clean_sales, clean_staff

    sales_c = clean_sales(sales_raw)
    inv_c = clean_inventory(inventory_raw)
    staff_c = clean_staff(staff_raw)
    mkt_c = clean_marketing(marketing_raw)
    aud_c = clean_audit(audit_raw)

    kpi = compute_outlet_kpis(sales_c, inv_c, staff_c, mkt_c, aud_c)
    assert len(kpi) == 3
    assert set(kpi["outlet_id"]) == {"OUT-01", "OUT-02", "OUT-03"}

    scores = calculate_performance_scores(kpi)
    assert scores["performance_score"].between(0, 100).all()
    # OUT-01 should be healthiest due to higher revenue + low wastage + low absenteeism
    best = scores.sort_values("performance_score", ascending=False).iloc[0]["outlet_id"]
    assert best == "OUT-01"


def test_forecast_features(sales_raw: pd.DataFrame) -> None:
    from data_engine.cleaning import clean_sales

    sales_c = clean_sales(sales_raw)
    feat = build_forecast_features(sales_c)
    # Should have lag columns
    assert "lag_1" in feat.columns
    assert len(feat) > 0


def test_forecast_train_and_save(sales_raw: pd.DataFrame) -> None:
    from data_engine.cleaning import clean_sales

    sales_c = clean_sales(sales_raw)
    model, cols = train_forecast_model(sales_c)
    assert len(cols) > 0
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "model.joblib"
        save_model(model, p)
        loaded = load_model(p)
        assert loaded is not None


def test_pipeline_end_to_end(sales_raw: pd.DataFrame, inventory_raw: pd.DataFrame, staff_raw: pd.DataFrame, marketing_raw: pd.DataFrame, audit_raw: pd.DataFrame) -> None:
    output = run_outlet_intelligence_pipeline(sales_raw, inventory_raw, staff_raw, marketing_raw, audit_raw)
    assert output.outlet_count == 3
    assert len(output.kpis) == 3
    assert len(output.performance_scores) == 3
    assert len(output.forecasts) == 3
    for fc in output.forecasts:
        assert len(fc.forecasts) == 7
    assert len(output.root_causes) == 3
    # JSON serialisable
    j = output.to_json_dict()
    assert "kpis" in j
    assert j["outlet_count"] == 3


def test_pipeline_empty_raises() -> None:
    empty = pd.DataFrame()
    with pytest.raises(ValueError):
        run_outlet_intelligence_pipeline(empty, empty, empty, empty, empty)


def test_root_cause_wastage_flag(inventory_raw: pd.DataFrame, sales_raw: pd.DataFrame, staff_raw: pd.DataFrame, marketing_raw: pd.DataFrame, audit_raw: pd.DataFrame) -> None:
    output = run_outlet_intelligence_pipeline(sales_raw, inventory_raw, staff_raw, marketing_raw, audit_raw)
    # OUT-02 has high wastage -> should have Inventory issue
    rc_map = {rc.outlet_id: rc for rc in output.root_causes}
    out02_issues = [i.domain for i in rc_map["OUT-02"].issues]
    assert "Inventory" in out02_issues


def test_type_error_on_non_dataframe(sales_raw: pd.DataFrame) -> None:
    with pytest.raises(TypeError):
        run_outlet_intelligence_pipeline("not a df", sales_raw, sales_raw, sales_raw, sales_raw)  # type: ignore[arg-type]
