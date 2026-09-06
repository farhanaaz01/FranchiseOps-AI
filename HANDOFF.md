# FranchiseOps AI — Data Analysis Engineer Handoff

**Package:** `data_engine/`  **Entry point:** `run_outlet_intelligence_pipeline`  
**Stack:** Python 3.11, pandas, pydantic v2, scikit-learn, XGBoost, joblib

---

## 1. What each module does

| Module | Role |
|---|---|
| `config.py` | Single source for *every* threshold, weight and hyper-parameter. No magic numbers elsewhere. Edit here to retune without touching logic. |
| `schemas.py` | Pydantic models for every input/output. Reuse directly as FastAPI `response_model` — no translation layer. |
| `cleaning.py` | Five pure functions `clean_sales/inventory/staff/marketing/audit(df) -> df`. Domain-aware imputation: sales uses 7-day centered rolling median per outlet; inventory rebuilds `closing_stock` from the flow equation `opening + received - consumed - wastage`. No file/DB I/O. |
| `kpi_engine.py` | `compute_outlet_kpis(*cleaned)` merges per-domain KPIs (outer join, neutral defaults) and `calculate_performance_scores(kpi_df)` blends them into a 0-100 score `0.35*revenue +0.15*growth +0.15*wastage(inv)+0.15*absenteeism(inv)+0.10*compliance+0.10*roi` (min-max normalised across the cohort) + `Healthy / At Risk / Critical` classification. |
| `ml_models.py` | Forecasting regressor (`XGBRegressor n_estimators=200 max_depth=4`) on lag `[1,7,14]` + rolling `[7,14]` + `dow` features, and risk classifier (`XGBClassifier n_estimators=100 max_depth=3`). Train and predict are separate; `save_model`/`load_model` via joblib. Falls back to sklearn `GradientBoosting` if xgboost not installed. |
| `root_cause_engine.py` | Rule scan per outlet: `wastage>3%`, `peak_understaffed>15%`, `absenteeism>10%`, `compliance<75`, `growth<0%`, `roi<0%`, `stockout<3 days cover`. Issues sorted `critical > high > medium > low`; `build_recommendation` turns top 2 into a sentence. Deterministic/auditable. |
| `pipeline.py` | **Orchestrator** — `run_outlet_intelligence_pipeline(sales, inventory, staff, marketing, audit) -> PipelineOutput`. Calls cleaning → KPIs → scoring → ML → root-cause and returns the Pydantic envelope (JSON-serialisable via `.model_dump(mode="json")`). |
| `tests/test_pipeline.py` | pytest suite on synthetic 3-outlet / 30-day data. Covers imputation, scoring bounds, forecast 7-day shape, root-cause triggers, empty/type errors, joblib round-trip. |

---

## 2. Single entry point

```python
from data_engine.pipeline import run_outlet_intelligence_pipeline
import pandas as pd

output = run_outlet_intelligence_pipeline(
    sales,       # pd.DataFrame
    inventory,   # pd.DataFrame
    staff,       # pd.DataFrame
    marketing,   # pd.DataFrame
    audit,       # pd.DataFrame
)

# FastAPI wiring example
from fastapi import APIRouter
from data_engine.schemas import PipelineOutput

router = APIRouter()

@router.post("/intelligence/run", response_model=PipelineOutput)
def run_intelligence(
    sales: list[dict], inventory: list[dict], staff: list[dict],
    marketing: list[dict], audit: list[dict],
):
    import pandas as pd
    return run_outlet_intelligence_pipeline(
        pd.DataFrame(sales), pd.DataFrame(inventory),
        pd.DataFrame(staff), pd.DataFrame(marketing), pd.DataFrame(audit),
    )

# JSON for frontend / LLM layer
payload = output.model_dump(mode="json")
# or
payload = output.to_json_dict()
```

Returns a `PipelineOutput` with `generated_at`, `outlet_count`, `kpis`, `performance_scores`, `forecasts` (7 per outlet), `risk_predictions`, `feature_importances`, `root_causes`.

---

## 3. Expected input schema

All inputs are **DataFrames** (no file paths). Reading CSVs / querying Postgres happens *outside* the pipeline — pass the resulting DataFrames in. Column names are case-sensitive; extra columns are ignored/preserved where noted.

**sales** — `outlet_id: str`, `date: date|str (parseable)`, `revenue: float` (negative allowed — treated as refund glitch -> NaN). Optional extras preserved.

**inventory** — `outlet_id: str`, `opening_stock: float`, `received_qty: float`, `consumed_qty: float`, `wastage_qty: float`, `closing_stock: float|NaN`. Missing `closing_stock` is reconstructed.

**staff** — `outlet_id: str`, `date?: date`, `scheduled: int`, `present: int`, `absent?: int` (derived if missing), `is_peak_understaffed?: bool`.

**marketing** — `outlet_id: str`, `campaign_cost` (or `cost`) `float`, `revenue_attributed?: float`, `roi` (or `campaign_roi`) `float|%`. Missing `roi` derived as `(revenue-cost)/cost*100`.

**audit** — `outlet_id: str`, `compliance_score: float 0-100`, `violations?` / `violation_count?`. Missing score defaults to `75.0`.

All tables may contain duplicates — they are dropped. Outlets are unioned across tables (outer join) so an outlet appearing in any table is scored.

---

## 4. Expected output schema (JSON)

Top-level `PipelineOutput` fields:

```json
{
  "generated_at": "2026-09-03T00:00:00",
  "outlet_count": 3,
  "kpis": [{
    "outlet_id": "OUT-01",
    "avg_daily_revenue": 5234.5,
    "revenue_growth_pct": 12.3,
    "wastage_rate": 1.8,
    "absenteeism_rate": 6.0,
    "peak_understaffed_pct": 4.2,
    "compliance_score": 90.0,
    "campaign_roi": 60.0,
    "stockout_risk_flag": false
  }],
  "performance_scores": [{
    "outlet_id": "OUT-01",
    "performance_score": 78.4,
    "health_status": "Healthy",
    "components": {"avg_daily_revenue": 0.9, "revenue_growth_pct": 0.7}
  }],
  "forecasts": [{
    "outlet_id": "OUT-01",
    "forecasts": [
      {"outlet_id": "OUT-01", "forecast_date": "2026-09-04", "predicted_revenue": 5400.1, "model_version": "xgb-v1"}
    ],
    "trained_on_rows": 90,
    "generated_at": "2026-09-03T00:00:00"
  }],
  "risk_predictions": [{
    "outlet_id": "OUT-02",
    "risk_probability": 0.82,
    "predicted_label": "At Risk",
    "top_drivers": [{"feature": "wastage_rate", "importance": 0.35}]
  }],
  "feature_importances": [{"feature": "wastage_rate", "importance": 0.35}],
  "root_causes": [{
    "outlet_id": "OUT-02",
    "performance_score": 42.1,
    "health_status": "Critical",
    "issues": [{
      "domain": "Inventory", "severity": "high", "metric": "wastage_rate",
      "value": 5.4, "threshold": 3.0,
      "finding": "Inventory Agent: wastage 5.4% exceeds threshold (3.0%)",
      "recommendation": "Review Inventory: reduce wastage via FIFO checks..."
    }],
    "priority_issue": "Inventory Agent: wastage 5.4% exceeds threshold (3.0%)",
    "overall_recommendation": "Review Inventory: reduce wastage via FIFO checks... Also: increase peak-hour staffing..."
  }]
}
```

Pydantic models map 1:1 to FastAPI response models: `OutletKPI`, `PerformanceScore`, `ForecastPoint`/`ForecastResult`, `RiskPrediction`, `RiskFeatureImportance`, `RootCauseIssue`/`RootCauseFinding`, `PipelineOutput`.

---

## 5. Assumptions & limitations

- **Rolling median imputation needs ≥7 days of history** per outlet; outlets with <7 days or all-NaN revenue remain NaN then fall back to the outlet median. In production, back-fill from the DB before calling the pipeline.
- **Min-max normalisation is cohort-relative** (across the batch of outlets passed in). Scores are comparable *within* a call but shift if the outlet set changes. For stable absolute scoring, normalise against a fixed reference cohort.
- **Health cut-offs:** `Healthy ≥70`, `At Risk 50-70`, `Critical <50` (from `config.HEALTH_THRESHOLDS`). Adjust in `config.py` if the business team defines different bands.
- **Risk classifier is honestly scoped:** with 20 outlets at a single latest snapshot it is good for *feature-importance-driven explanation*, not held-out prediction. With a single class (all Healthy) the pipeline returns uniform `risk_probability=0.1` + a note in `feature_importances` instead of failing. Production should train on outlet-week snapshots (thousands of rows) and persist the model with `save_model`.
- **Forecasting needs ≥20 feature rows** after warm-up; otherwise `train_forecast_model` raises and the pipeline falls back to a flat forecast (last known revenue carried forward 7 days).
- **Root-cause thresholds are business-tuned defaults** in `config.ROOT_CAUSE_THRESHOLDS` — override there, not inline.
- **No I/O inside core logic:** the pipeline never reads CSVs or hits Postgres. Swap in `SQLAlchemy` queries by passing `pd.read_sql(...)` DataFrames to the same entry point.
- **XGBoost fallback:** if `xgboost` is not installed, the ML layer falls back to `sklearn.ensemble.GradientBoosting*` with the same interface so tests/demo still pass.

---

## 6. Quick start

```bash
pip install -r requirements.txt
pytest data_engine/tests -v          # or: python -m pytest data_engine/tests -v
python -c "from data_engine.pipeline import run_outlet_intelligence_pipeline; help(run_outlet_intelligence_pipeline)"
```

### Demo scripts (not part of the core package)

Three helper scripts at the project root generate sample data, run the pipeline
end-to-end, and produce a viewable dashboard. These are demo/dev tooling only —
`data_engine/` itself has no dependency on them.

```bash
python generate_sample_data.py   # writes sample_data/*.csv (5 outlets, 60 days)
python run_pipeline_demo.py      # runs the pipeline on that data, writes
                                  #   pipeline_output.json + dashboard.html
```

`dashboard.html` is a single self-contained file (charting library is bundled
inline, no CDN or internet connection needed) — open it directly in a browser
to see outlet scorecards, a performance-score comparison, a health-status
breakdown, and a daily-revenue distribution, all built from the pipeline's
own output.

To rebuild just the dashboard from an existing `pipeline_output.json` (e.g.
after wiring the pipeline to real data instead of the sample generator), run:

```bash
python generate_dashboard.py
```

It reads `pipeline_output.json` and `sample_data/sales.csv` and regenerates
`dashboard.html` from `dashboard_template.html`. Swap in your own JSON/CSV
paths via `build_dashboard(pipeline_output_path=..., sales_csv_path=...)` if
your data lives elsewhere.
