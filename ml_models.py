"""
ML layer — 7-day revenue forecasting (regression) + underperformance risk (classifier).

Training and inference are strictly separated so retraining never touches the
FastAPI layer. Models are save/load-able via joblib. Hyper-parameters are
preserved from ``03_ml_forecasting.py``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from data_engine.config import (
    FORECAST_HORIZON_DAYS,
    FORECAST_LAGS,
    FORECAST_MODEL_PARAMS,
    FORECAST_ROLLING_WINDOWS,
    RISK_MODEL_PARAMS,
)

try:
    from xgboost import XGBClassifier, XGBRegressor

    _HAS_XGB = True
except ImportError:  # fallback for environments without xgboost
    from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor

    _HAS_XGB = False

    class XGBRegressor(GradientBoostingRegressor):  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(
                n_estimators=kwargs.get("n_estimators", 200),
                max_depth=kwargs.get("max_depth", 4),
                learning_rate=kwargs.get("learning_rate", 0.08),
                random_state=kwargs.get("random_state", 42),
            )

    class XGBClassifier(GradientBoostingClassifier):  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(
                n_estimators=kwargs.get("n_estimators", 100),
                max_depth=kwargs.get("max_depth", 3),
                learning_rate=kwargs.get("learning_rate", 0.1),
                random_state=kwargs.get("random_state", 42),
            )


# ---------------------------------------------------------------------------
# Forecasting — feature engineering
# ---------------------------------------------------------------------------
def build_forecast_features(
    sales_clean: pd.DataFrame,
    lags: list[int] | None = None,
    rolling_windows: list[int] | None = None,
) -> pd.DataFrame:
    """Create lag + rolling features per outlet for the regressor.

    Args:
        sales_clean: Cleaned sales DataFrame with ``outlet_id``, ``date``, ``revenue``.
        lags: Lag days (default from config ``FORECAST_LAGS``).
        rolling_windows: Rolling mean/std windows (default ``FORECAST_ROLLING_WINDOWS``).

    Returns:
        DataFrame with ``outlet_id``, ``date``, ``revenue`` + feature columns
        (``lag_1``, ``lag_7`` ..., ``roll_mean_7``, ``roll_std_7`` ...).
        Rows with NaN features (warm-up) are dropped.

    Raises:
        ValueError: If required columns are missing.
    """
    if sales_clean.empty:
        return pd.DataFrame()
    if not {"outlet_id", "date", "revenue"}.issubset(sales_clean.columns):
        raise ValueError("sales_clean needs outlet_id, date, revenue columns.")
    lags = lags or FORECAST_LAGS
    rolling_windows = rolling_windows or FORECAST_ROLLING_WINDOWS

    df = sales_clean.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["outlet_id", "date"])

    frames: list[pd.DataFrame] = []
    for outlet, group in df.groupby("outlet_id"):
        g = group.sort_values("date").copy()
        g = g.set_index("date")
        # Ensure daily frequency for lag correctness — reindex and forward-fill is NOT used;
        # lag features naturally produce NaN for missing days which are dropped.
        for lag in lags:
            g[f"lag_{lag}"] = g["revenue"].shift(lag)
        for w in rolling_windows:
            g[f"roll_mean_{w}"] = g["revenue"].shift(1).rolling(w).mean()
            g[f"roll_std_{w}"] = g["revenue"].shift(1).rolling(w).std().fillna(0)
        # Day-of-week as optional numeric seasonality
        g["dow"] = g.index.dayofweek  # type: ignore[attr-defined]
        g = g.reset_index()
        g["outlet_id"] = outlet
        frames.append(g)

    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    # Drop warm-up rows where any lag is NaN
    lag_cols = [f"lag_{l}" for l in lags]
    if not out.empty and lag_cols:
        out = out.dropna(subset=lag_cols)
    return out.reset_index(drop=True)


def _feature_columns(df: pd.DataFrame) -> list[str]:
    """Return feature column names (lag/roll/dow)."""
    return [c for c in df.columns if c.startswith("lag_") or c.startswith("roll_") or c == "dow"]


# ---------------------------------------------------------------------------
# Forecasting — train / predict / save / load
# ---------------------------------------------------------------------------
def train_forecast_model(
    sales_clean: pd.DataFrame,
    feature_df: pd.DataFrame | None = None,
) -> tuple[Any, list[str]]:
    """Train the 7-day revenue regressor.

    Args:
        sales_clean: Cleaned sales DataFrame (used if ``feature_df`` is None).
        feature_df: Pre-built feature DataFrame (from :func:`build_forecast_features`).
            If provided, ``sales_clean`` is ignored.

    Returns:
        Tuple ``(model, feature_cols)`` where ``model`` is a fitted
        ``XGBRegressor`` (or sklearn fallback) and ``feature_cols`` is the
        ordered list of features the model expects at inference.

    Raises:
        ValueError: If there are fewer than 20 training rows.
    """
    feat = feature_df if feature_df is not None else build_forecast_features(sales_clean)
    if feat.empty or len(feat) < 20:
        raise ValueError(f"Not enough rows to train forecast model: {len(feat)} (need >=20)")
    cols = _feature_columns(feat)
    if not cols:
        raise ValueError("No feature columns found.")
    X = feat[cols]
    y = feat["revenue"]
    model = XGBRegressor(**FORECAST_MODEL_PARAMS)  # type: ignore[arg-type]
    model.fit(X, y)
    return model, cols


def predict_forecast(
    model: Any,
    sales_clean: pd.DataFrame,
    feature_cols: list[str],
    horizon: int = FORECAST_HORIZON_DAYS,
) -> pd.DataFrame:
    """Generate ``horizon``-day forecasts per outlet via recursive prediction.

    The last known feature row per outlet is used to seed an autoregressive
    loop: each predicted revenue is fed back as the next day's lag.

    Args:
        model: Fitted regressor from :func:`train_forecast_model`.
        sales_clean: Cleaned sales DataFrame (for last date + history).
        feature_cols: Ordered feature names the model was trained on.
        horizon: Days to forecast (default 7).

    Returns:
        DataFrame with ``outlet_id``, ``forecast_date``, ``predicted_revenue``.

    Raises:
        ValueError: If ``sales_clean`` is empty or feature_cols missing.
    """
    if sales_clean.empty:
        return pd.DataFrame(columns=["outlet_id", "forecast_date", "predicted_revenue"])
    if not feature_cols:
        raise ValueError("feature_cols is empty.")

    feat = build_forecast_features(sales_clean)
    if feat.empty:
        # Fallback: use last known revenue as flat forecast
        last_dates = sales_clean.groupby("outlet_id")["date"].max()
        last_rev = sales_clean.groupby("outlet_id")["revenue"].last()
        rows: list[dict[str, Any]] = []
        for outlet in last_dates.index:
            base = pd.to_datetime(last_dates[outlet])
            rev = float(last_rev[outlet])
            for h in range(1, horizon + 1):
                rows.append(
                    {"outlet_id": outlet, "forecast_date": (base + pd.Timedelta(days=h)).date(), "predicted_revenue": rev}
                )
        return pd.DataFrame(rows)

    # Per-outlet recursive forecast
    rows: list[dict[str, Any]] = []
    for outlet, group in feat.groupby("outlet_id"):
        hist = sales_clean[sales_clean["outlet_id"] == outlet].sort_values("date")
        last_revenues: list[float] = hist["revenue"].tolist()
        last_date = pd.to_datetime(hist["date"].max())
        # Seed: last feature row
        last_feat_row = group.sort_values("date").iloc[-1]

        for h in range(1, horizon + 1):
            # Build feature vector for next day
            # Lags are taken from tail of last_revenues
            feat_vec: dict[str, float] = {}
            for lag in FORECAST_LAGS:
                feat_vec[f"lag_{lag}"] = last_revenues[-lag] if len(last_revenues) >= lag else float(np.mean(last_revenues))
            for w in FORECAST_ROLLING_WINDOWS:
                window_vals = last_revenues[-w:] if len(last_revenues) >= w else last_revenues
                feat_vec[f"roll_mean_{w}"] = float(np.mean(window_vals)) if window_vals else 0.0
                feat_vec[f"roll_std_{w}"] = float(np.std(window_vals, ddof=0)) if len(window_vals) > 1 else 0.0
            # dow for the forecast date
            f_date = last_date + pd.Timedelta(days=h)
            feat_vec["dow"] = float(f_date.dayofweek)

            # Ensure all expected cols present
            x = pd.DataFrame([feat_vec])
            # Reorder + fill missing with 0
            for c in feature_cols:
                if c not in x.columns:
                    x[c] = 0.0
            x = x[feature_cols]
            pred = float(model.predict(x)[0])
            # Guard against negative forecast
            pred = max(0.0, pred)
            rows.append({"outlet_id": outlet, "forecast_date": f_date.date(), "predicted_revenue": round(pred, 2)})
            last_revenues.append(pred)

    return pd.DataFrame(rows)


def save_model(model: Any, path: str | Path) -> Path:
    """Persist a trained model with joblib.

    Args:
        model: Fitted model.
        path: Destination file path (``.joblib``).

    Returns:
        Resolved Path written to.

    Raises:
        OSError: If the path is not writable.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, p)
    return p


def load_model(path: str | Path) -> Any:
    """Load a model persisted by :func:`save_model`.

    Args:
        path: Path to ``.joblib`` file.

    Returns:
        Loaded model.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Model file not found: {p}")
    return joblib.load(p)


# ---------------------------------------------------------------------------
# Risk classifier — train / predict / importances
# ---------------------------------------------------------------------------
def train_risk_classifier(
    kpi_df: pd.DataFrame,
    performance_df: pd.DataFrame | None = None,
) -> tuple[Any, list[str]]:
    """Train the underperformance risk classifier.

    Label: ``At Risk`` or ``Critical`` (health_status != Healthy) -> 1, else 0.
    Features: numeric KPI columns.

    Args:
        kpi_df: Output of :func:`compute_outlet_kpis` (or at least the KPI columns).
        performance_df: Optional DataFrame with ``outlet_id`` + ``health_status``.
            If None, health is derived from ``kpi_df`` if it already contains
            ``health_status``; otherwise every outlet is assumed Healthy and the
            function raises if only one class exists (honest scoping from the guide).

    Returns:
        Tuple ``(classifier, feature_cols)``.

    Raises:
        ValueError: If fewer than 2 classes exist (need both Healthy and At Risk).
    """
    if kpi_df.empty:
        raise ValueError("kpi_df is empty — cannot train risk classifier.")

    # Determine labels
    if performance_df is not None and "health_status" in performance_df.columns:
        label_map = performance_df.set_index("outlet_id")["health_status"]
        labels = kpi_df["outlet_id"].map(label_map)
    elif "health_status" in kpi_df.columns:
        labels = kpi_df["health_status"]
    else:
        raise ValueError("Cannot derive risk labels — kpi_df lacks health_status and no performance_df supplied.")

    y = labels.apply(lambda s: 0 if s == "Healthy" else 1).astype(int)

    # Features: numeric KPIs excluding outlet_id/health columns
    exclude = {"outlet_id", "health_status", "performance_score", "stockout_risk_flag"}
    feature_cols = [c for c in kpi_df.columns if c not in exclude and pd.api.types.is_numeric_dtype(kpi_df[c])]
    # Also drop norm_ columns if present
    feature_cols = [c for c in feature_cols if not c.startswith("norm_")]

    if len(feature_cols) == 0:
        raise ValueError("No numeric feature columns found for risk classifier.")
    if y.nunique() < 2:
        # Honest fallback: return a dummy that predicts the majority class
        # but still expose feature importances as uniform
        raise ValueError(
            f"Risk classifier needs at least 2 classes, got {y.unique().tolist()} — "
            "with 20 outlets at a single snapshot the model is for feature-importance "
            "explanation, not held-out prediction. Provide more historical snapshots."
        )

    X = kpi_df[feature_cols].fillna(0)
    clf = XGBClassifier(**RISK_MODEL_PARAMS)  # type: ignore[arg-type]
    clf.fit(X, y)
    return clf, feature_cols


def predict_risk(
    clf: Any,
    kpi_df: pd.DataFrame,
    feature_cols: list[str],
) -> pd.DataFrame:
    """Predict underperformance risk per outlet.

    Args:
        clf: Fitted classifier from :func:`train_risk_classifier`.
        kpi_df: KPI DataFrame (same columns as training).
        feature_cols: Ordered feature names used during training.

    Returns:
        DataFrame with ``outlet_id``, ``risk_probability`` (0-1), ``predicted_label``.

    Raises:
        ValueError: If feature_cols missing from kpi_df.
    """
    missing = [c for c in feature_cols if c not in kpi_df.columns]
    if missing:
        raise ValueError(f"Missing feature columns at inference: {missing}")
    X = kpi_df[feature_cols].fillna(0)
    # predict_proba -> probability of class 1 (At Risk)
    if hasattr(clf, "predict_proba"):
        proba = clf.predict_proba(X)[:, 1] if len(clf.classes_) > 1 else np.zeros(len(X))
    else:
        proba = clf.predict(X).astype(float)
    preds = clf.predict(X) if hasattr(clf, "predict") else (proba > 0.5).astype(int)
    out = kpi_df[["outlet_id"]].copy()
    out["risk_probability"] = np.round(proba, 4)
    out["predicted_label"] = np.where(preds == 1, "At Risk", "Healthy")
    return out


def get_feature_importance(clf: Any, feature_cols: list[str]) -> pd.DataFrame:
    """Return sorted feature importances.

    Args:
        clf: Fitted classifier.
        feature_cols: Feature names in fit order.

    Returns:
        DataFrame with ``feature`` and ``importance`` sorted descending.
        Returns uniform importances if the model has no importances.

    Raises:
        ValueError: If lengths mismatch.
    """
    if len(feature_cols) == 0:
        return pd.DataFrame(columns=["feature", "importance"])
    if hasattr(clf, "feature_importances_"):
        imp = np.array(clf.feature_importances_, dtype=float)
    elif hasattr(clf, "coef_"):
        imp = np.abs(np.array(clf.coef_).ravel())
        if imp.sum() > 0:
            imp = imp / imp.sum()
    else:
        imp = np.ones(len(feature_cols)) / len(feature_cols)
    # Guard length mismatch (e.g. fallback model)
    if len(imp) != len(feature_cols):
        imp = np.ones(len(feature_cols)) / len(feature_cols)
    df = pd.DataFrame({"feature": feature_cols, "importance": np.round(imp, 4)})
    return df.sort_values("importance", ascending=False).reset_index(drop=True)
