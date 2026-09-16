"""Builds structured audit reports."""
from datetime import datetime
from typing import List, Dict, Any

from audit_agent.models.schemas import Violation, CorrectiveAction


def generate_report(outlet_id: str,
                    outlet_meta: Dict[str, Any],
                    compliance: Dict[str, Any],
                    violations: List[Violation],
                    risk: Dict[str, Any],
                    corrective_actions: List[CorrectiveAction],
                    data_limitations: List[str]) -> Dict[str, Any]:
    dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for v in violations:
        dist[v.severity] = dist.get(v.severity, 0) + 1

    return {
        "audit_id": f"AUDIT-{outlet_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "outlet": outlet_meta,
        "audit_period": _period(compliance.get("checks", [])),
        "overall_compliance_score": compliance.get("compliance_score"),
        "compliance_status": compliance.get("classification"),
        "checks_summary": {
            "total": compliance.get("total_checks"),
            "compliant": compliance.get("compliant_checks"),
            "non_compliant": compliance.get("non_compliant_checks"),
            "unknown": compliance.get("unknown_checks"),
        },
        "violations": [v.__dict__ for v in violations],
        "severity_distribution": dist,
        "major_findings": [v.description for v in violations if v.severity in ("HIGH", "CRITICAL")],
        "risk_level": risk.get("risk_level"),
        "risk_reasons": risk.get("reasons"),
        "corrective_actions": [c.__dict__ for c in corrective_actions],
        "pending_corrective_actions": [c.__dict__ for c in corrective_actions if c.status == "PENDING"],
        "recommendations": _recommendations(violations, risk),
        "data_limitations": data_limitations,
        "generated_at": datetime.utcnow().isoformat(),
    }


def _period(checks: List[Dict[str, Any]]) -> Dict[str, Any]:
    dates = [c.get("date") for c in checks if c.get("date")]
    if not dates:
        return {"start": None, "end": None}
    return {"start": min(dates), "end": max(dates)}


def _recommendations(violations: List[Violation], risk: Dict[str, Any]) -> List[str]:
    recs = []
    if any(v.severity == "CRITICAL" for v in violations):
        recs.append("Escalate critical violations to the Human Head immediately for approval.")
    if risk.get("risk_level") in ("HIGH", "CRITICAL"):
        recs.append("Schedule a follow-up audit within 7 days.")
    cats = {v.category for v in violations}
    for c in cats:
        recs.append(f"Review {c} procedures with outlet manager.")
    if not recs:
        recs.append("No corrective recommendations — outlet is compliant.")
    return recs