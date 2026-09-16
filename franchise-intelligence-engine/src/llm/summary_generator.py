"""Generates executive summary — deterministic, optionally LLM-enhanced."""
from __future__ import annotations
from typing import Dict, Any


class SummaryGenerator:
    def __init__(self, llm_client=None):
        self.llm = llm_client

    def generate(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        health = analysis.get("franchise_health", {})
        risks = analysis.get("risks", [])
        opps = analysis.get("opportunities", [])
        recs = analysis.get("recommendations", [])

        summary = {
            "overall_health": {
                "score": health.get("overall_score"),
                "status": health.get("status"),
                "partial_data": health.get("partial_data", False),
            },
            "key_positives": self._positives(analysis),
            "key_problems": self._problems(analysis),
            "emerging_risks": [r["description"] for r in risks[:5]],
            "growth_opportunities": [o["opportunity"] for o in opps[:5]],
            "recommended_priorities": [r["recommendation"] for r in recs[:5]],
        }

        if self.llm and self.llm.available:
            narrative = self._llm_narrative(summary, analysis)
            if narrative:
                summary["narrative"] = narrative
        return summary

    def _positives(self, a):
        return [f"{o['outlet_id']}: {o['opportunity']}" for o in a.get("opportunities", [])[:3]]

    def _problems(self, a):
        return [r["description"] for r in a.get("risks", [])[:3]]

    def _llm_narrative(self, summary: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        prompt = (
            "You are a franchise operations analyst. Write a concise executive summary "
            "based ONLY on the structured data below. Do NOT invent numbers. "
            "Keep under 200 words.\n\n"
            f"Health: {summary['overall_health']}\n"
            f"Top risks: {summary['emerging_risks']}\n"
            f"Opportunities: {summary['growth_opportunities']}\n"
            f"Recommendations: {summary['recommended_priorities']}\n"
        )
        return self.llm.generate(prompt) or ""