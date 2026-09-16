"""Natural-language query -> intent mapping."""
from __future__ import annotations
from typing import Dict, Any


INTENT_KEYWORDS = {
    "franchise_health": ["how is the franchise", "overall franchise health",
                          "franchise performing", "health score"],
    "at_risk_outlets": ["which outlets are at risk", "at risk", "at-risk outlets"],
    "biggest_problems": ["biggest problems", "top problems", "major issues"],
    "best_outlet": ["performing best", "top outlet", "best outlet"],
    "needs_attention": ["needs immediate attention", "immediate attention"],
    "risks": ["what risks", "predict", "risks"],
    "opportunities": ["growth opportunities", "opportunities"],
    "compare_outlets": ["compare all outlets", "compare outlets"],
    "recommendations": ["strategic recommendations", "top 5", "recommendations"],
    "common_issues": ["common across multiple outlets", "common issues"],
    "urgent_attention": ["immediate human head", "urgent attention"],
    "action_plan": ["strategic action plan", "action plan"],
    "explain_decline": ["why has franchise health declined", "explain decline"],
}


class QueryHandler:
    def __init__(self, llm_client=None):
        self.llm = llm_client

    def classify_intent(self, query: str) -> str:
        q = query.lower().strip()
        for intent, keywords in INTENT_KEYWORDS.items():
            if any(k in q for k in keywords):
                return intent
        # Fallback to LLM if available
        if self.llm and self.llm.available:
            prompt = (
                "Classify the following franchise operations question into exactly ONE of these intents: "
                f"{list(INTENT_KEYWORDS.keys())}.\n\n"
                f"Question: {query}\nAnswer with just the intent name."
            )
            result = self.llm.generate(prompt)
            if result:
                candidate = result.strip().lower().replace(" ", "_")
                if candidate in INTENT_KEYWORDS:
                    return candidate
        return "franchise_health"