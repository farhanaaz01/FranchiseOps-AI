"""
generate_dashboard.py
-----------------------
Builds a self-contained dashboard.html by injecting the latest
pipeline_output.json and raw daily sales figures into dashboard_template.html.

The template has Chart.js bundled inline (no internet connection needed to
view it), so the output file works standalone: double-click it, or open it
in any browser, even offline.

Run directly:
    python generate_dashboard.py

Or import and call build_dashboard() from another script (run_pipeline_demo.py
does this automatically after every pipeline run).
"""

from __future__ import annotations

import csv
import json
import os

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(BASE_DIR, "dashboard_template.html")
OUTPUT_PATH = os.path.join(BASE_DIR, "dashboard.html")
PIPELINE_OUTPUT_PATH = os.path.join(BASE_DIR, "pipeline_output.json")
SALES_CSV_PATH = os.path.join(BASE_DIR, "sample_data", "sales.csv")


def _load_sales_rows(path: str) -> list[dict]:
    """Read the raw sales CSV into a list of {outlet_id, date, revenue} dicts,
    used for the daily-revenue histogram. Returns [] if the file is missing
    so dashboard generation never hard-fails just because sample data wasn't
    regenerated."""
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rev = r.get("revenue", "")
            try:
                value = None if rev in ("", "nan", "NaN") else float(rev)
            except ValueError:
                value = None
            rows.append({"outlet_id": r.get("outlet_id"), "date": r.get("date"), "revenue": value})
    return rows


def build_dashboard(
    pipeline_output_path: str = PIPELINE_OUTPUT_PATH,
    sales_csv_path: str = SALES_CSV_PATH,
    template_path: str = TEMPLATE_PATH,
    output_path: str = OUTPUT_PATH,
) -> str:
    """Inject pipeline output + raw sales rows into the dashboard template.

    Returns the path to the written dashboard.html file.
    Raises FileNotFoundError if pipeline_output.json or the template is missing
    (both are required; sales.csv is optional -> histogram just shows no data).
    """
    if not os.path.exists(pipeline_output_path):
        raise FileNotFoundError(
            f"{pipeline_output_path} not found. Run `python run_pipeline_demo.py` first."
        )
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"{template_path} not found.")

    with open(pipeline_output_path) as f:
        pipeline_output = json.load(f)

    sales_rows = _load_sales_rows(sales_csv_path)

    with open(template_path) as f:
        html = f.read()

    html = html.replace("__PIPELINE_JSON__", json.dumps(pipeline_output))
    html = html.replace("__SALES_JSON__", json.dumps(sales_rows))

    with open(output_path, "w") as f:
        f.write(html)

    return output_path


def main():
    path = build_dashboard()
    size_kb = os.path.getsize(path) / 1024
    print(f"Dashboard written to: {path}  ({size_kb:.0f} KB)")
    print("Open it directly in a browser -- no server or internet connection needed.")


if __name__ == "__main__":
    main()
