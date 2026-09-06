# Prompt for Antigravity — Data Analysis Engineer Module (FranchiseOps AI)

Copy everything below into Antigravity as your task prompt.

---

## PROMPT START

You are acting as a senior Python backend engineer. I am the Data Analysis
Engineer on a project called **FranchiseOps AI** — an agentic franchise
management platform. My code needs to be handed off to a teammate who will
integrate it into our FastAPI backend, so it must be **modular, typed,
documented, and import-ready** — not a collection of standalone scripts.

### Project context

- Backend stack: Python + FastAPI, PostgreSQL + SQLAlchemy, Pydantic schemas
- Agentic layer: LangGraph, with specialized agents (Outlet, Inventory, Staff,
  Marketing, Audit) reporting into a central "Franchise Intelligence Engine"
- My responsibility (Data Analysis Engineer) covers the data + ML layer:
  1. Data cleaning of raw operational tables (sales, inventory, staff,
     marketing, audit)
  2. KPI calculation and a composite outlet performance score (0-100),
     with Healthy / At Risk / Critical classification
  3. ML models: 7-day revenue forecasting (regression) and an
     underperformance risk model with feature importances
  4. A rule-based root-cause reasoning engine that scans KPIs across all
     domains and outputs structured JSON findings + recommendations
     (this JSON is what the LLM layer turns into natural-language
     explanations for the dashboard)

### What I need you to build

Convert my existing logic (I will paste my working scripts below) into a
clean Python package with this structure:

```
data_engine/
├── __init__.py
├── config.py              # thresholds, weights, constants — no magic numbers inline
├── schemas.py              # Pydantic models for every input/output (for FastAPI reuse)
├── cleaning.py             # data cleaning functions, one per table
├── kpi_engine.py            # KPI calculation + performance scoring
├── ml_models.py             # forecasting model + risk classifier, trainable & loadable
├── root_cause_engine.py     # cross-domain rule-based reasoning
├── pipeline.py              # orchestrator: raw data in -> final JSON out, one call
└── tests/
    └── test_pipeline.py     # pytest unit tests with small sample data
```

### Hard requirements

1. **Every public function must have type hints and a docstring** (args,
   returns, raises) — my teammate is integrating this without me in the room.
2. **No hardcoded file paths.** All functions take DataFrames or Pydantic
   models as arguments and return DataFrames or Pydantic models — I/O
   (reading CSVs, DB calls) stays out of the core logic so it can be swapped
   for PostgreSQL queries later.
3. **Expose one top-level orchestrator function** (`run_outlet_intelligence_pipeline`)
   that takes the five raw tables and returns the final structured JSON —
   this is the single entry point my teammate wires into a FastAPI route.
4. **Pydantic schemas for every output** (OutletKPI, PerformanceScore,
   ForecastResult, RootCauseFinding) so they map directly onto FastAPI
   response models without translation work.
5. **Keep the ML layer swappable**: model training and model inference must
   be separate functions, with the trained model save/load-able (joblib),
   so retraining doesn't require touching the API layer.
6. **Preserve my existing logic exactly** — thresholds, scoring weights,
   and the imputation approach (rolling-median for sales, flow-equation
   reconstruction for stock) must not change, only be restructured.
7. **Add a `requirements.txt`** listing exact packages used.
8. **Add a short `HANDOFF.md`** explaining: what each module does, the
   single entry point to call, expected input schema, expected output
   schema, and any assumptions/limitations (e.g. the risk classifier is
   trained on outlet-snapshot data and works best with more historical rows).

### My existing code (convert this — do not redesign the logic)

```python
# [PASTE the contents of generate_dataset.py, 01_data_cleaning.py,
#  02_kpi_engine.py, 03_ml_forecasting.py, and 04_root_cause_engine.py here]
```

### Output format

Give me the full package as separate files (one file per module, clearly
labeled with its path), followed by the `requirements.txt` and `HANDOFF.md`.
Do not truncate or summarize any file — I need complete, working code I can
hand to my teammate as-is.

## PROMPT END

---

### How to use this

1. Open each of your five script files (`generate_dataset.py`,
   `01_data_cleaning.py`, `02_kpi_engine.py`, `03_ml_forecasting.py`,
   `04_root_cause_engine.py`) and paste their full contents into the
   placeholder section above.
2. Paste the whole prompt into Antigravity.
3. Review the output package before handing it off — check that
   `pipeline.py`'s entry point signature matches what your backend teammate
   expects (ask them what raw data format they'll be passing in: DataFrames,
   dicts, or DB query results).
4. Hand over the `data_engine/` folder + `HANDOFF.md` as your deliverable.
