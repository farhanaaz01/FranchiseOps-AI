"""Growth opportunity detection from positive/improving findings."""
from __future__ import annotations
from typing import List, Dict, Any
from src.contracts.finding import Finding


class OpportunityDetector:
    def detect(self, findings: List[Finding]) -> List[Dict[str, Any]]:
        opps: List[Dict[str, Any]] = []

        for f in findings:
            is_positive = (
                f.finding_type == "OPPORTUNITY"
                or f.trend == "IMPROVING"
                or f.severity == "LOW" and self._beats_baseline(f)
            )
            if not is_positive:
                continue
            opps.append({
                "opportunity": self._title(f),
                "outlet_id": f.outlet_id or "FRANCHISE_WIDE",
                "category": f.category,
                "supporting_evidence": f.evidence or [f.description],
                "expected_benefit": self._benefit(f),
                "confidence": f.confidence,
                "suggested_next_step": self._next_step(f),
                "source_finding_id": f.finding_id,
            })

        opps.sort(key=lambda x: x["confidence"], reverse=True)
        return opps

    def _beats_baseline(self, f: Finding) -> bool:
        try:
            if f.value is None or f.baseline is None:
                return False
            return float(f.value) > float(f.baseline)
        except (TypeError, ValueError):
            return False

    def _title(self, f: Finding) -> str:
        return f"Leverage strength in {f.category} ({f.metric}) at {f.outlet_id or 'franchise'}"

    def _benefit(self, f: Finding) -> str:
        cat = f.category.lower()
        return {
            "sales": "Replicate top-performer tactics across outlets.",
            "marketing": "Expand campaign strategy; increase ROI.",
            "workforce": "Use as training benchmark for other outlets.",
            "inventory": "Standardize best-in-class inventory practices.",
            "compliance": "Use as compliance benchmark.",
        }.get(cat, "Potential performance uplift.")

    def _next_step(self, f: Finding) -> str:
        return "Human Head to review and consider pilot replication."