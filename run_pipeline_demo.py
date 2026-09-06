"""
run_pipeline_demo.py
---------------------
Loads the CSVs produced by generate_sample_data.py and runs them through
the single entry point: data_engine.pipeline.run_outlet_intelligence_pipeline

Run:
    python generate_sample_data.py     # once, to create sample_data/*.csv
    python run_pipeline_demo.py        # runs the pipeline and prints/saves JSON

Output:
    pipeline_output.json  (written next to this script)
"""

from __future__ import annotations

import json
import os
import sys

import pandas as pd

from data_engine.pipeline import run_outlet_intelligence_pipeline
from generate_dashboard import build_dashboard

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "sample_data")


def load_csv(name: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        print(f"Missing {path}. Run `python generate_sample_data.py` first.")
        sys.exit(1)
    return pd.read_csv(path)


def main():
    sales = load_csv("sales.csv")
    inventory = load_csv("inventory.csv")
    staff = load_csv("staff.csv")
    marketing = load_csv("marketing.csv")
    audit = load_csv("audit.csv")

    print(f"Loaded: sales={len(sales)} inventory={len(inventory)} "
          f"staff={len(staff)} marketing={len(marketing)} audit={len(audit)} rows")

    output = run_outlet_intelligence_pipeline(sales, inventory, staff, marketing, audit)
    payload = output.model_dump(mode="json")

    out_path = os.path.join(BASE_DIR, "pipeline_output.json")
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\nPipeline ran successfully. Outlets scored: {payload['outlet_count']}")
    print("\n--- Performance summary ---")
    for ps in payload["performance_scores"]:
        print(f"  {ps['outlet_id']:8s} score={ps['performance_score']:6.1f}  status={ps['health_status']}")

    print("\n--- Top root-cause per outlet ---")
    for rc in payload["root_causes"]:
        print(f"  {rc['outlet_id']:8s} {rc['health_status']:10s} priority: {rc['priority_issue']}")

    print(f"\nFull JSON output written to: {out_path}")

    dashboard_path = build_dashboard(pipeline_output_path=out_path)
    print(f"Dashboard regenerated: {dashboard_path}")
    print("Open dashboard.html in any browser to view it -- it's self-contained, no server needed.")


if __name__ == "__main__":
    main()
