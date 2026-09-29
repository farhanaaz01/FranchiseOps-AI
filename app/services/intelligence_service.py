"""Franchise Intelligence Engine — DB → data_engine pipeline → cached output."""

from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from data_engine.pipeline import run_outlet_intelligence_pipeline
from data_engine.schemas import PipelineOutput, RootCauseFinding

from pathlib import Path

import pandas as pd

from app.models import IntelligencePipelineRun
from app.services import pipeline_data_service
from app.utils.outlet_id import format_pipeline_outlet_id, parse_pipeline_outlet_id

_latest_cache: PipelineOutput | None = None
_SAMPLE_DIR = Path(__file__).resolve().parents[2] / "sample_data"


def _frames_all_empty(*frames: pd.DataFrame) -> bool:
    return all(getattr(df, "empty", True) for df in frames)


def _load_sample_pipeline_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sales = pd.read_csv(_SAMPLE_DIR / "sales.csv")
    inventory = pd.read_csv(_SAMPLE_DIR / "inventory.csv")
    staff = pd.read_csv(_SAMPLE_DIR / "staff.csv")
    marketing = pd.read_csv(_SAMPLE_DIR / "marketing.csv")
    audit = pd.read_csv(_SAMPLE_DIR / "audit.csv")
    return sales, inventory, staff, marketing, audit


def _load_from_db(db: Session) -> PipelineOutput | None:
    run = (
        db.query(IntelligencePipelineRun)
        .filter(IntelligencePipelineRun.is_latest.is_(True))
        .order_by(IntelligencePipelineRun.run_id.desc())
        .first()
    )
    if not run or not run.output_json:
        return None
    data = json.loads(run.output_json)
    return PipelineOutput.model_validate(data)


def _persist_run(db: Session, output: PipelineOutput) -> IntelligencePipelineRun:
    db.query(IntelligencePipelineRun).filter(IntelligencePipelineRun.is_latest.is_(True)).update(
        {"is_latest": False}
    )
    run = IntelligencePipelineRun(
        generated_at=output.generated_at,
        outlet_count=output.outlet_count,
        output_json=json.dumps(output.model_dump(mode="json")),
        is_latest=True,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def run_pipeline(db: Session) -> PipelineOutput:
    global _latest_cache
    sales, inventory, staff, marketing, audit = pipeline_data_service.build_all_pipeline_inputs(db)
    if _frames_all_empty(sales, inventory, staff, marketing, audit) and _SAMPLE_DIR.exists():
        sales, inventory, staff, marketing, audit = _load_sample_pipeline_inputs()
    output = run_outlet_intelligence_pipeline(sales, inventory, staff, marketing, audit)
    _persist_run(db, output)
    _latest_cache = output
    return output


def get_latest(db: Session) -> PipelineOutput:
    global _latest_cache
    if _latest_cache is not None:
        return _latest_cache
    cached = _load_from_db(db)
    if cached is not None:
        _latest_cache = cached
        return cached
    return run_pipeline(db)


def get_root_causes(db: Session, outlet_id: str | None = None) -> list[RootCauseFinding]:
    output = get_latest(db)
    findings = output.root_causes
    if not outlet_id:
        return findings
    needle = outlet_id.strip().upper()
    if not needle.startswith("OUT-"):
        parsed = parse_pipeline_outlet_id(needle)
        if parsed is not None:
            needle = format_pipeline_outlet_id(parsed)
    return [f for f in findings if f.outlet_id.upper() == needle]


def get_forecasts(db: Session, outlet_id: str | None = None):
    output = get_latest(db)
    forecasts = output.forecasts
    if not outlet_id:
        return forecasts
    needle = outlet_id.strip().upper()
    if not needle.startswith("OUT-"):
        parsed = parse_pipeline_outlet_id(needle)
        if parsed is not None:
            needle = format_pipeline_outlet_id(parsed)
    return [f for f in forecasts if f.outlet_id.upper() == needle]
