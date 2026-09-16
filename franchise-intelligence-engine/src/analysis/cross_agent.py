"""Cross-agent correlation detection (non-causal)."""
from __future__ import annotations
from typing import List, Dict, Any
from src.contracts.finding import Finding


CORRELATION_PATTERNS = [
    {
        "id": "SALES_INVENTORY",
        "categories": {"sales", "inventory"},
        "note": "Sales and inventory findings co-occur at the same outlet.",
        "hypothesis": "The findings suggest a possible relationship between stockouts and declining sales.",
    },
    {
        "id": "WORKFORCE_PERFORMANCE",
        "categories": {"workforce", "sales"},
        "note": "Workforce issues align with performance decline.",
        "hypothesis": "Staff shortages may be associated with declining outlet productivity.",
    },
    {
        "id": "MARKETING_SALES",
        "categories": {"marketing", "sales"},
        "note": "Marketing and sales move together.",
        "hypothesis": "High campaign engagement with low conversion may indicate a funnel issue.",
    },
    {
        "id": "AUDIT_PERFORMANCE",
        "categories": {"compliance", "sales"},
        "note": "Compliance issues align with performance decline.",
        "hypothesis": "Repeated compliance violations may coincide with deteriorating outlet performance.",
    },
    {
        "id": "INVENTORY_MARKETING",
        "categories": {"inventory", "marketing"},
        "note": "Marketing spikes may outpace inventory.",
        "hypothesis": "Successful promotions may strain insufficient inventory.",
    },
]


class CrossAgentAnalyzer:
    def analyze(self, findings: List[Finding]) -> List[Dict[str, Any]]:
        by_outlet: Dict[str, List[Finding]] = {}
        for f in findings:
            if f.outlet_id:
                by_outlet.setdefault(f.outlet_id, []).append(f)

        insights: List[Dict[str, Any]] = []
        for outlet_id, items in by_outlet.items():
            cats = {f.category for f in items}
            for pattern in CORRELATION_PATTERNS:
                if pattern["categories"].issubset(cats):
                    involved = [f for f in items if f.category in pattern["categories"]]
                    negative = [f for f in involved
                                if f.severity in ("HIGH", "CRITICAL") or f.trend == "DECLINING"]
                    if len(negative) >= 2:
                        avg_conf = sum(f.confidence for f in involved) / len(involved)
                        insights.append({
                            "type": "POSSIBLE_RELATIONSHIP",
                            "pattern_id": pattern["id"],
                            "outlet_id": outlet_id,
                            "categories": sorted(pattern["categories"]),
                            "note": pattern["note"],
                            "hypothesis": pattern["hypothesis"],
                            "supporting_findings": [f.finding_id for f in involved],
                            "evidence_strength": "STRONG" if len(negative) >= 3 else "MODERATE",
                            "confidence": round(min(0.95, avg_conf), 2),
                            "disclaimer": "Correlation ≠ causation. Verified only through further analysis.",
                        })
        return insights