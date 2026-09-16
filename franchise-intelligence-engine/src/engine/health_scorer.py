"""Deterministic health score calculations."""
from __future__ import annotations
from typing import List, Dict, Any
from src.contracts.finding import Finding


SEVERITY_PENALTY = {"LOW": 0, "MEDIUM": 10, "HIGH": 25, "CRITICAL": 45, "UNKNOWN": 5}
TREND_ADJ = {"IMPROVING": +5, "STABLE": 0, "DECLINING": -5, "UNKNOWN": 0}

CATEGORY_TO_DIMENSION = {
    "sales": "outlet_performance",
    "performance": "outlet_performance",
    "inventory": "inventory",
    "workforce": "workforce",
    "staff": "workforce",
    "marketing": "marketing",
    "compliance": "compliance",
    "audit": "compliance",
}


class HealthScorer:
    def __init__(self, config: dict):
        self.config = config

    def score_dimension(self, dimension: str, findings: List[Finding]) -> Dict[str, Any]:
        relevant = [f for f in findings
                    if CATEGORY_TO_DIMENSION.get(f.category, f.category) == dimension]
        if not relevant:
            return {"score": None, "status": "DATA_UNAVAILABLE",
                    "findings_count": 0, "contribution": 0.0}

        total_penalty = 0.0
        for f in relevant:
            penalty = SEVERITY_PENALTY.get(f.severity, 5)
            adj = TREND_ADJ.get(f.trend, 0)
            confidence_weight = f.confidence
            total_penalty += max(0, penalty - adj) * confidence_weight

        avg_penalty = total_penalty / max(1, len(relevant))
        score = max(0.0, min(100.0, 100.0 - avg_penalty))
        return {
            "score": round(score, 2),
            "status": self._status(score),
            "findings_count": len(relevant),
            "contribution": 0.0,  # filled later
        }

    def score_franchise(self, findings: List[Finding]) -> Dict[str, Any]:
        weights = self.config["dimension_weights"]
        dims = list(weights.keys())
        dim_scores: Dict[str, Any] = {}
        for d in dims:
            dim_scores[d] = self.score_dimension(d, findings)

        # Determine available dimensions
        available = {d: v for d, v in dim_scores.items() if v["score"] is not None}
        unavailable = [d for d in dims if d not in available]

        warnings = []
        partial = False
        if unavailable:
            partial = True
            warnings.append(
                f"Dimensions unavailable (no data): {', '.join(unavailable)}. "
                "Overall score is based on PARTIAL data."
            )

        if available:
            total_weight = sum(weights[d] for d in available)
            overall = 0.0
            for d, v in available.items():
                w = weights[d] / total_weight if total_weight else 0
                v["contribution"] = round(w * v["score"], 2)
                overall += v["contribution"]
            overall = round(overall, 2)
        else:
            overall = None

        status = self._status(overall) if overall is not None else "DATA_UNAVAILABLE"

        strengths = [d for d, v in available.items() if v["score"] >= 70]
        weaknesses = [d for d, v in available.items() if v["score"] < 55]

        return {
            "overall_score": overall,
            "status": status,
            "dimension_scores": dim_scores,
            "strongest_dimensions": strengths,
            "weakest_dimensions": weaknesses,
            "partial_data": partial,
            "warnings": warnings,
        }

    def _status(self, score: float) -> str:
        t = self.config["health_thresholds"]
        if score >= t["EXCELLENT"]: return "EXCELLENT"
        if score >= t["HEALTHY"]: return "HEALTHY"
        if score >= t["STABLE"]: return "STABLE"
        if score >= t["AT_RISK"]: return "AT_RISK"
        return "CRITICAL"