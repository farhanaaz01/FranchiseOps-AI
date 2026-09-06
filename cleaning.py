"""
Data cleaning — one pure function per table, no I/O, no hardcoded paths.

Preserves the exact logic from ``01_data_cleaning.py``:
* sales: drop_duplicates, negative revenue -> NaN -> 7-day rolling median per outlet
* inventory: rebuild closing_stock from flow equation
All functions take a DataFrame and return a cleaned DataFrame.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from data_engine.config import (
    ROLLING_MEDIAN_CENTER,
    ROLLING_MEDIAN_MIN_PERIODS,
    ROLLING_MEDIAN_WINDOW,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _require_columns(df: pd.DataFrame, cols: list[str], table: str) -> None:
    """Raise a clear error if expected columns are missing.

    Args:
        df: Input DataFrame.
        cols: Required column names.
        table: Human-readable table name for the error.

    Raises:
        ValueError: If any required column is absent.
    """
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{table} missing required columns: {missing}. Got {list(df.columns)}")


# ---------------------------------------------------------------------------
# sales
# ---------------------------------------------------------------------------
def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the sales table with domain-aware imputation.

    Logic preserved from the original script:
    1. Drop exact duplicates.
    2. Negative ``revenue`` (refund glitches) is invalid -> set to NaN.
    3. Impute NaN revenue with a 7-day rolling median per ``outlet_id``
       (centered window, min_periods=1, via ``groupby.transform``).

    Args:
        df: Raw sales DataFrame. Expected columns: ``outlet_id``, ``date``,
            ``revenue``. Extra columns are preserved.

    Returns:
        Cleaned DataFrame with no duplicate rows and no negative revenue.
        Rows where revenue cannot be imputed (all-NaN group) remain NaN.

    Raises:
        ValueError: If required columns are missing.
    """
    if df.empty:
        return df.copy()
    _require_columns(df, ["outlet_id", "revenue"], "sales")
    cleaned = df.drop_duplicates().copy()

    # Ensure date is datetime for stable sort/groupby
    if "date" in cleaned.columns:
        cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
        cleaned = cleaned.sort_values(["outlet_id", "date"])

    # Negative revenue -> NaN (domain rule)
    cleaned.loc[cleaned["revenue"] < 0, "revenue"] = np.nan

    # 7-day rolling median per outlet (centered) — vectorised via transform
    # Note: rolling needs a sorted series per group. We use transform with
    # a lambda that applies rolling median.
    def _rolling_median(s: pd.Series) -> pd.Series:
        return s.fillna(
            s.rolling(
                window=ROLLING_MEDIAN_WINDOW,
                center=ROLLING_MEDIAN_CENTER,
                min_periods=ROLLING_MEDIAN_MIN_PERIODS,
            ).median()
        )

    cleaned["revenue"] = cleaned.groupby("outlet_id")["revenue"].transform(_rolling_median)

    # Second pass: any remaining NaN at edges (all-NaN group) -> group median
    cleaned["revenue"] = cleaned.groupby("outlet_id")["revenue"].transform(
        lambda s: s.fillna(s.median())
    )

    return cleaned.reset_index(drop=True)


# ---------------------------------------------------------------------------
# inventory — flow-equation reconstruction
# ---------------------------------------------------------------------------
def clean_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Clean inventory movements and reconstruct ``closing_stock``.

    Flow equation (preserved)::
        closing_stock = opening_stock + received_qty - consumed_qty - wastage_qty

    Missing ``closing_stock`` is filled from the equation. Remaining NaNs
    in qty columns are filled with 0 (no movement). Negative qty values are
    coerced to NaN then to 0 after a warning-free clip.

    Args:
        df: Raw inventory DataFrame with ``outlet_id``, ``opening_stock``,
            ``received_qty``, ``consumed_qty``, ``wastage_qty``, ``closing_stock``.

    Returns:
        Cleaned DataFrame with consistent stock arithmetic.

    Raises:
        ValueError: If required columns are missing.
    """
    if df.empty:
        return df.copy()
    _require_columns(
        df,
        ["outlet_id", "opening_stock", "received_qty", "consumed_qty", "wastage_qty", "closing_stock"],
        "inventory",
    )
    cleaned = df.drop_duplicates().copy()

    # Coerce negatives to NaN then to 0 — negatives are data-entry errors
    qty_cols = ["opening_stock", "received_qty", "consumed_qty", "wastage_qty"]
    for col in qty_cols:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
        cleaned.loc[cleaned[col] < 0, col] = np.nan

    cleaned["closing_stock"] = pd.to_numeric(cleaned["closing_stock"], errors="coerce")

    # Flow-based reconstruction for missing closing_stock
    flow_value = (
        cleaned["opening_stock"].fillna(0)
        + cleaned["received_qty"].fillna(0)
        - cleaned["consumed_qty"].fillna(0)
        - cleaned["wastage_qty"].fillna(0)
    )
    cleaned["closing_stock"] = cleaned["closing_stock"].fillna(flow_value)

    # Fill any remaining NaN qty with 0 (no movement on that day)
    for col in qty_cols:
        cleaned[col] = cleaned[col].fillna(0).clip(lower=0)

    # If closing_stock still NaN (all inputs NaN) -> 0
    cleaned["closing_stock"] = cleaned["closing_stock"].fillna(0).clip(lower=0)

    return cleaned.reset_index(drop=True)


# ---------------------------------------------------------------------------
# staff
# ---------------------------------------------------------------------------
def clean_staff(df: pd.DataFrame) -> pd.DataFrame:
    """Clean staff attendance table.

    * Drop duplicates.
    * Coerce ``scheduled``/``present``/``absent`` to numeric.
    * Re-derive ``absent`` if inconsistent (``absent != scheduled-present``).
    * Fill NaN ``is_peak_understaffed`` with False.
    * Clip rates to [0, scheduled].

    Args:
        df: Raw staff DataFrame. Expected: ``outlet_id``, ``date``,
            ``scheduled``, ``present``. Optional ``is_peak_understaffed``.

    Returns:
        Cleaned staff DataFrame.

    Raises:
        ValueError: If required columns are missing.
    """
    if df.empty:
        return df.copy()
    _require_columns(df, ["outlet_id", "scheduled", "present"], "staff")
    cleaned = df.drop_duplicates().copy()

    for col in ["scheduled", "present"]:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0).clip(lower=0)

    # Derive absent if missing or inconsistent
    if "absent" not in cleaned.columns:
        cleaned["absent"] = cleaned["scheduled"] - cleaned["present"]
    else:
        cleaned["absent"] = pd.to_numeric(cleaned["absent"], errors="coerce")
        derived = cleaned["scheduled"] - cleaned["present"]
        # Use derived where absent is NaN or mismatched by >0.5
        mask = cleaned["absent"].isna() | (abs(cleaned["absent"] - derived) > 0.5)
        cleaned.loc[mask, "absent"] = derived[mask]
    cleaned["absent"] = cleaned["absent"].clip(lower=0)

    if "is_peak_understaffed" in cleaned.columns:
        cleaned["is_peak_understaffed"] = cleaned["is_peak_understaffed"].infer_objects(copy=False).fillna(False).astype(bool)
    else:
        cleaned["is_peak_understaffed"] = False

    if "date" in cleaned.columns:
        cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")

    return cleaned.reset_index(drop=True)


# ---------------------------------------------------------------------------
# marketing
# ---------------------------------------------------------------------------
def clean_marketing(df: pd.DataFrame) -> pd.DataFrame:
    """Clean marketing campaign table.

    * Drop duplicates.
    * Coerce cost/revenue columns to numeric, negatives -> NaN -> 0.
    * Re-derive ``roi`` if missing: ``(revenue-campaign_cost)/campaign_cost*100``.

    Args:
        df: Raw marketing DataFrame. Expected: ``outlet_id``, ``campaign_cost``
            or ``cost``, and optionally ``revenue_attributed`` / ``roi``.

    Returns:
        Cleaned marketing DataFrame.

    Raises:
        ValueError: If outlet_id is missing.
    """
    if df.empty:
        return df.copy()
    _require_columns(df, ["outlet_id"], "marketing")
    cleaned = df.drop_duplicates().copy()

    # Normalise column alias: cost -> campaign_cost
    if "campaign_cost" not in cleaned.columns and "cost" in cleaned.columns:
        cleaned = cleaned.rename(columns={"cost": "campaign_cost"})

    for col in ["campaign_cost", "revenue_attributed", "roi", "campaign_roi"]:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    if "campaign_cost" in cleaned.columns:
        cleaned.loc[cleaned["campaign_cost"] < 0, "campaign_cost"] = np.nan
        cleaned["campaign_cost"] = cleaned["campaign_cost"].fillna(0)

    if "roi" not in cleaned.columns and "campaign_roi" in cleaned.columns:
        cleaned = cleaned.rename(columns={"campaign_roi": "roi"})

    # Derive roi where missing and cost > 0
    if "roi" in cleaned.columns and "revenue_attributed" in cleaned.columns:
        mask = cleaned["roi"].isna() & (cleaned["campaign_cost"] > 0)
        cleaned.loc[mask, "roi"] = (
            (cleaned.loc[mask, "revenue_attributed"] - cleaned.loc[mask, "campaign_cost"])
            / cleaned.loc[mask, "campaign_cost"]
            * 100
        )
        cleaned["roi"] = cleaned["roi"].fillna(0)
    elif "roi" in cleaned.columns:
        cleaned["roi"] = cleaned["roi"].fillna(0)

    return cleaned.reset_index(drop=True)


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------
def clean_audit(df: pd.DataFrame) -> pd.DataFrame:
    """Clean audit/compliance table.

    * Drop duplicates.
    * Coerce ``compliance_score`` to numeric, clip to [0, 100].
    * Coerce ``violations`` to int.

    Args:
        df: Raw audit DataFrame. Expected: ``outlet_id``, ``compliance_score``.

    Returns:
        Cleaned audit DataFrame.

    Raises:
        ValueError: If required columns are missing.
    """
    if df.empty:
        return df.copy()
    _require_columns(df, ["outlet_id"], "audit")
    cleaned = df.drop_duplicates().copy()

    if "compliance_score" in cleaned.columns:
        cleaned["compliance_score"] = pd.to_numeric(cleaned["compliance_score"], errors="coerce")
        cleaned["compliance_score"] = cleaned["compliance_score"].clip(lower=0, upper=100).fillna(75.0)
    else:
        cleaned["compliance_score"] = 75.0

    if "violations" in cleaned.columns:
        cleaned["violations"] = pd.to_numeric(cleaned["violations"], errors="coerce").fillna(0).astype(int)
    elif "violation_count" in cleaned.columns:
        cleaned["violations"] = pd.to_numeric(cleaned["violation_count"], errors="coerce").fillna(0).astype(int)

    if "date" in cleaned.columns:
        cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")

    return cleaned.reset_index(drop=True)
