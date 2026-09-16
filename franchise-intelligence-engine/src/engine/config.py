"""Config loader."""
from pathlib import Path
import yaml


DEFAULT_CONFIG = {
    "dimension_weights": {
        "outlet_performance": 0.30,
        "inventory": 0.20,
        "workforce": 0.20,
        "marketing": 0.15,
        "compliance": 0.15,
    },
    "health_thresholds": {
        "EXCELLENT": 85, "HEALTHY": 70, "STABLE": 55, "AT_RISK": 40, "CRITICAL": 0,
    },
    "risk_thresholds": {"CRITICAL": 80, "HIGH": 60, "MEDIUM": 40, "LOW": 0},
    "data_freshness_days": 7,
}


def load_config(path: str = "config.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        return DEFAULT_CONFIG
    try:
        loaded = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception as e:
        print(f"[WARN] Failed to load {path}: {e}. Using defaults.")
        return DEFAULT_CONFIG
    cfg = {**DEFAULT_CONFIG, **loaded}
    return cfg