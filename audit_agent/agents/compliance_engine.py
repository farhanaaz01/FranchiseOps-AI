"""Deterministic compliance scoring and check evaluation."""
from datetime import datetime
from typing import List, Dict, Any, Tuple

from audit_agent.config import SEVERITY_WEIGHTS, SCORE_BANDS


def _to_bool(v: Any) -> bool | None:
    if isinstance(v, bool):
        return v
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "y", "t"):
        return True
    if s in ("false", "0", "no", "n", "f"):
        return False
    return None


def _compare(actual: Any, expected: Any, operator: str) -> bool | None:
    """Returns True/False if comparable, None if insufficient data."""
    if actual is None or actual == "":
        return None
    if operator == "eq":
        a, e = _to_bool(actual), _to_bool(expected)
        if a is None or e is None:
            return None
        return a == e
    if operator == "ne":
        a, e = _to_bool(actual), _to_bool(expected)
        if a is None or e is None:
            return None
        return a != e
    try:
        return float(actual) >= float(expected) if operator == "gte" else float(actual) <= float(expected)
    except (TypeError, ValueError):
        return None


def evaluate_check(record: Dict[str, Any], rule: Dict[str, Any]) -> str:
    """Return COMPLIANT / NON_COMPLIANT / UNKNOWN."""
    field = rule.get("field")
    if not field or field not in record:
        return "UNKNOWN"
    result = _compare(record.get(field), rule.get("expected"), rule.get("operator", "eq"))
    if result is None:
        return "UNKNOWN"
    return "COMPLIANT" if result else "NON_COMPLIANT"


def calculate_compliance_score(outlet_records: List[Dict[str, Any]],
                               rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Weighted compliance score = sum(weight of compliant) / sum(weight of applicable) * 100
    Only COMPLIANT and NON_COMPLIANT count toward denominator. UNKNOWN excluded.
    """
    total_weight = 0.0
    compliant_weight = 0.0
    checks = []

    for rec in outlet_records:
        for rule in rules:
            status = evaluate_check(rec, rule)
            weight = float(rule.get("weight", 1.0))
            entry = {
                "record_id": rec.get("record_id"),
                "date": rec.get("date"),
                "rule_id": rule.get("rule_id"),
                "rule_name": rule.get("name"),
                "status": status,
                "weight": weight,
                "severity": rule.get("severity", "MEDIUM"),
            }
            checks.append(entry)
            if status == "COMPLIANT":
                compliant_weight += weight
                total_weight += weight
            elif status == "NON_COMPLIANT":
                total_weight += weight
            # UNKNOWN excluded

    score = (compliant_weight / total_weight * 100.0) if total_weight > 0 else 0.0
    band = classify_score(score)

    return {
        "compliance_score": round(score, 2),
        "classification": band,
        "total_checks": len(checks),
        "comparable_checks": sum(1 for c in checks if c["status"] != "UNKNOWN"),
        "compliant_checks": sum(1 for c in checks if c["status"] == "COMPLIANT"),
        "non_compliant_checks": sum(1 for c in checks if c["status"] == "NON_COMPLIANT"),
        "unknown_checks": sum(1 for c in checks if c["status"] == "UNKNOWN"),
        "checks": checks,
    }


def classify_score(score: float) -> str:
    for threshold, label in SCORE_BANDS:
        if score >= threshold:
            return label
    return "CRITICAL"