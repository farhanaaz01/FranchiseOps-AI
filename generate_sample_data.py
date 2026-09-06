"""
generate_sample_data.py
------------------------
Creates realistic synthetic CSVs for 5 outlets x 60 days, matching the
column names expected by `data_engine` (see HANDOFF.md, section 3).

Run:
    python generate_sample_data.py

Produces (in ./sample_data/):
    sales.csv, inventory.csv, staff.csv, marketing.csv, audit.csv

These files are then consumed by run_pipeline_demo.py.
"""

from __future__ import annotations

import os
import random
from datetime import date, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

OUTLETS = ["OUT-01", "OUT-02", "OUT-03", "OUT-04", "OUT-05"]
DAYS = 60
START_DATE = date(2026, 7, 1)

# Give each outlet a distinct "personality" so results are interesting:
#   OUT-01: healthy, growing
#   OUT-02: struggling (high wastage, understaffed) -> should surface as At Risk / Critical
#   OUT-03: average, stable
#   OUT-04: healthy but flat growth
#   OUT-05: patchy data (some missing values) to exercise the cleaning logic
OUTLET_PROFILES = {
    "OUT-01": dict(base_rev=6000, growth=0.35, wastage=1.5, absent=4, understaffed=3, compliance=92, roi=70),
    "OUT-02": dict(base_rev=4000, growth=-0.20, wastage=6.5, absent=14, understaffed=22, compliance=60, roi=-15),
    "OUT-03": dict(base_rev=5000, growth=0.05, wastage=2.5, absent=7, understaffed=8, compliance=80, roi=25),
    "OUT-04": dict(base_rev=7000, growth=0.01, wastage=2.0, absent=5, understaffed=5, compliance=88, roi=40),
    "OUT-05": dict(base_rev=4500, growth=0.10, wastage=3.0, absent=8, understaffed=10, compliance=75, roi=20),
}


def daterange(n_days: int):
    return [START_DATE + timedelta(days=i) for i in range(n_days)]


def build_sales() -> pd.DataFrame:
    rows = []
    for outlet in OUTLETS:
        prof = OUTLET_PROFILES[outlet]
        for i, d in enumerate(daterange(DAYS)):
            trend = prof["base_rev"] * (1 + prof["growth"] * (i / DAYS))
            dow_boost = 1.15 if d.weekday() in (4, 5) else 1.0  # weekend bump
            noise = np.random.normal(0, prof["base_rev"] * 0.06)
            revenue = max(0, trend * dow_boost + noise)

            # inject occasional data-quality issues to exercise cleaning.py
            if outlet == "OUT-05" and random.random() < 0.08:
                revenue = np.nan  # missing reading
            elif random.random() < 0.02:
                revenue = -abs(revenue)  # refund glitch -> should become NaN then imputed

            rows.append({"outlet_id": outlet, "date": d.isoformat(), "revenue": round(revenue, 2)})
    return pd.DataFrame(rows)


def build_inventory() -> pd.DataFrame:
    rows = []
    for outlet in OUTLETS:
        prof = OUTLET_PROFILES[outlet]
        opening = 500.0
        for d in daterange(DAYS):
            received = round(np.random.uniform(80, 150), 1)
            consumed = round(np.random.uniform(90, 140), 1)
            wastage_pct = prof["wastage"] / 100
            wastage = round(consumed * wastage_pct, 2)
            closing = round(opening + received - consumed - wastage, 2)

            row = {
                "outlet_id": outlet,
                "date": d.isoformat(),
                "opening_stock": opening,
                "received_qty": received,
                "consumed_qty": consumed,
                "wastage_qty": wastage,
                "closing_stock": closing,
            }
            # leave some closing_stock values blank so cleaning.py reconstructs them
            if random.random() < 0.10:
                row["closing_stock"] = np.nan

            rows.append(row)
            opening = closing if not np.isnan(closing) else opening
    return pd.DataFrame(rows)


def build_staff() -> pd.DataFrame:
    rows = []
    for outlet in OUTLETS:
        prof = OUTLET_PROFILES[outlet]
        for d in daterange(DAYS):
            scheduled = random.randint(8, 12)
            absent_prob = prof["absent"] / 100
            absent = 1 if random.random() < absent_prob else 0
            present = scheduled - absent
            is_peak_understaffed = random.random() < (prof["understaffed"] / 100)

            rows.append(
                {
                    "outlet_id": outlet,
                    "date": d.isoformat(),
                    "scheduled": scheduled,
                    "present": present,
                    "absent": absent,
                    "is_peak_understaffed": is_peak_understaffed,
                }
            )
    return pd.DataFrame(rows)


def build_marketing() -> pd.DataFrame:
    rows = []
    for outlet in OUTLETS:
        prof = OUTLET_PROFILES[outlet]
        # a handful of campaigns per outlet over the period, not daily
        n_campaigns = random.randint(3, 6)
        for _ in range(n_campaigns):
            cost = round(np.random.uniform(200, 1500), 2)
            roi_pct = prof["roi"] + np.random.normal(0, 8)
            revenue_attributed = round(cost * (1 + roi_pct / 100), 2)
            rows.append(
                {
                    "outlet_id": outlet,
                    "campaign_cost": cost,
                    "revenue_attributed": revenue_attributed,
                    "roi": round(roi_pct, 2),
                }
            )
    return pd.DataFrame(rows)


def build_audit() -> pd.DataFrame:
    rows = []
    for outlet in OUTLETS:
        prof = OUTLET_PROFILES[outlet]
        # a couple of audit snapshots per outlet
        for _ in range(2):
            score = max(0, min(100, prof["compliance"] + np.random.normal(0, 4)))
            violations = max(0, int(round((100 - score) / 10)))
            rows.append(
                {
                    "outlet_id": outlet,
                    "compliance_score": round(score, 1),
                    "violation_count": violations,
                }
            )
    return pd.DataFrame(rows)


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "sample_data")
    os.makedirs(out_dir, exist_ok=True)

    datasets = {
        "sales.csv": build_sales(),
        "inventory.csv": build_inventory(),
        "staff.csv": build_staff(),
        "marketing.csv": build_marketing(),
        "audit.csv": build_audit(),
    }

    for filename, df in datasets.items():
        path = os.path.join(out_dir, filename)
        df.to_csv(path, index=False)
        print(f"wrote {path}  ({len(df)} rows)")

    print("\nDone. Run `python run_pipeline_demo.py` to execute the pipeline on this data.")


if __name__ == "__main__":
    main()
