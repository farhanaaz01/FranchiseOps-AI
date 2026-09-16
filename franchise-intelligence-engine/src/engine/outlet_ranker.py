"""Outlet-level scoring & ranking."""
from __future__ import annotations
from typing import List, Dict, Any
from src.contracts.finding import Finding
from src.engine.health_scorer import HealthScorer


class OutletRanker:
    def __init__(self, config: dict):
        self.config = config
        self.scorer = HealthScorer(config)

    def rank(self, findings: List[Finding]) -> Dict[str, Any]:
        by_outlet: Dict[str, List[Finding]] = {}
        for f in findings:
            if f.outlet_id:
                by_outlet.setdefault(f.outlet_id, []).append(f)

        outlet_scores = []
        for outlet_id, items in by_outlet.items():
            s = self.scorer.score_franchise(items)
            outlet_scores.append({
                "outlet_id": outlet_id,
                "overall_score": s["overall_score"],
                "status": s["status"],
                "dimension_scores": {d: v["score"] for d, v in s["dimension_scores"].items()},
                "findings_count": len(items),
                "strengths": s["strongest_dimensions"],
                "weaknesses": s["weakest_dimensions"],
            })

        ranked = sorted(
            outlet_scores,
            key=lambda x: (x["overall_score"] is not None, x["overall_score"] or 0),
            reverse=True,
        )

        # Most improved / declining — by count of IMPROVING vs DECLINING trends
        for entry in ranked:
            items = by_outlet[entry["outlet_id"]]
            entry["improving_count"] = sum(1 for f in items if f.trend == "IMPROVING")
            entry["declining_count"] = sum(1 for f in items if f.trend == "DECLINING")

        most_improved = max(ranked, key=lambda x: x["improving_count"], default=None)
        most_declining = max(ranked, key=lambda x: x["declining_count"], default=None)

        return {
            "ranked_outlets": ranked,
            "top_performers": [r["outlet_id"] for r in ranked[:3]],
            "lowest_performers": [r["outlet_id"] for r in ranked[-3:]],
            "most_improved": most_improved["outlet_id"] if most_improved else None,
            "most_declining": most_declining["outlet_id"] if most_declining else None,
            "high_risk_outlets": [r["outlet_id"] for r in ranked
                                  if r["status"] in ("AT_RISK", "CRITICAL")],
        }