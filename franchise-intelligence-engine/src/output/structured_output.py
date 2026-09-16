"""Canonical structured output builder + proposed actions."""
from __future__ import annotations
from typing import Dict, Any, List
import uuid


CONSEQUENTIAL_ACTIONS = {
    "increase_marketing_budget",
    "place_inventory_order",
    "hire_employee",
    "fire_employee",
    "change_salary",
    "close_outlet",
    "open_outlet",
    "approve_investment",
    "approve_purchase",
    "change_pricing",
    "launch_paid_campaign",
    "sign_contract",
}


class StructuredOutputBuilder:
    def build(self,
              intent: str,
              franchise_health: Dict[str, Any],
              outlet_rankings: Dict[str, Any],
              risks: List[Dict[str, Any]],
              opportunities: List[Dict[str, Any]],
              cross_agent: List[Dict[str, Any]],
              recommendations: List[Dict[str, Any]],
              proposed_actions: List[Dict[str, Any]],
              data_quality: Dict[str, Any],
              executive_summary: Dict[str, Any],
              warnings: List[str]) -> Dict[str, Any]:

        requires_approval = any(a.get("requires_human_approval") for a in proposed_actions)

        return {
            "intent": intent,
            "franchise_health_score": franchise_health.get("overall_score"),
            "health_status": franchise_health.get("status"),
            "dimension_scores": {
                d: v.get("score") for d, v in franchise_health.get("dimension_scores", {}).items()
            },
            "outlet_rankings": outlet_rankings,
            "key_findings": {
                "total": data_quality.get("duplicates_count", 0) + 0,
                "data_quality": data_quality,
            },
            "cross_agent_insights": cross_agent,
            "risks": risks,
            "opportunities": opportunities,
            "recommendations": recommendations,
            "proposed_actions": proposed_actions,
            "requires_human_approval": requires_approval,
            "confidence": self._avg_confidence(risks, opportunities),
            "warnings": warnings,
            "data_limitations": data_quality.get("issues", []),
            "executive_summary": executive_summary,
        }

    def _avg_confidence(self, risks, opportunities) -> float:
        vals = [r.get("confidence", 0) for r in risks] + \
               [o.get("confidence", 0) for o in opportunities]
        if not vals:
            return 0.5
        return round(sum(vals) / len(vals), 2)


def build_proposed_action(action_type: str,
                          affected_outlet: str,
                          reason: str,
                          supporting_findings: List[str],
                          expected_benefit: str,
                          estimated_cost: float = None,
                          risks: List[str] = None,
                          priority: str = "MEDIUM",
                          confidence: float = 0.7) -> Dict[str, Any]:
    """Every consequential action MUST be PENDING_APPROVAL and never auto-executed."""
    action = {
        "action_id": f"ACT-{uuid.uuid4().hex[:8].upper()}",
        "action_type": action_type,
        "affected_outlet": affected_outlet,
        "reason": reason,
        "supporting_findings": supporting_findings,
        "expected_benefit": expected_benefit,
        "estimated_cost": estimated_cost,
        "risks": risks or [],
        "priority": priority,
        "confidence": confidence,
        "status": "PENDING_APPROVAL",
        "requires_human_approval": True,
        "executed": False,   # ALWAYS False — engine cannot execute
    }
    assert action["status"] == "PENDING_APPROVAL"
    assert action["executed"] is False
    return action