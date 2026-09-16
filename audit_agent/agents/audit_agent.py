"""Main Audit Agent — orchestrates everything. Never auto-executes consequential actions."""
import logging
from typing import List, Dict, Any, Optional

from audit_agent.data_access.base_provider import BaseDataProvider
from audit_agent.agents.compliance_engine import calculate_compliance_score
from audit_agent.agents.violation_detector import detect_violations, severity_distribution
from audit_agent.agents.risk_analyzer import calculate_risk
from audit_agent.agents.corrective_action_tracker import (
    build_corrective_actions, find_overdue_actions, build_proposed_actions, ActionExecutor
)
from audit_agent.agents.report_generator import generate_report
from audit_agent.utils.llm_interface import LLMInterface
from audit_agent.config import SEVERITY_WEIGHTS

logger = logging.getLogger(__name__)


class AuditAgent:
    def __init__(self, provider: BaseDataProvider, llm: Optional[LLMInterface] = None):
        self.provider = provider
        self.llm = llm or LLMInterface()
        self.executor = ActionExecutor()

    # ---------- data loading ----------
    def _load(self):
        outlets = {o["outlet_id"]: o for o in self.provider.get_outlets()}
        records = self.provider.get_operational_records()
        rules = self.provider.get_audit_rules()
        actions = self.provider.get_corrective_actions()
        return outlets, records, rules, actions

    # ---------- core analysis ----------
    def analyze_outlet(self, outlet_id: str) -> Dict[str, Any]:
        outlets, records, rules, actions = self._load()
        if outlet_id not in outlets:
            return self._error(f"Unknown outlet id: {outlet_id}")

        outlet_records = [r for r in records if str(r.get("outlet_id")) == str(outlet_id)]
        if not outlet_records:
            return self._error(f"No operational records for outlet {outlet_id}", outlet_id=outlet_id)

        compliance = calculate_compliance_score(outlet_records, rules)
        violations = detect_violations(outlet_id, outlet_records, rules)
        overdue = find_overdue_actions(actions)
        overdue_for_outlet = [a for a in overdue if str(a.get("outlet_id")) == str(outlet_id)]

        risk = calculate_risk(
            outlet_id=outlet_id,
            violations=violations,
            compliance_score=compliance["compliance_score"],
            previous_score=None,
            overdue_actions=len(overdue_for_outlet),
        )

        corrective = build_corrective_actions(violations)
        proposed = build_proposed_actions(violations)

        data_limitations = []
        if compliance["unknown_checks"] > 0:
            data_limitations.append(
                f"{compliance['unknown_checks']} check(s) skipped due to insufficient data."
            )

        report = generate_report(
            outlet_id=outlet_id,
            outlet_meta=outlets[outlet_id],
            compliance=compliance,
            violations=violations,
            risk=risk,
            corrective_actions=corrective,
            data_limitations=data_limitations,
        )

        facts_for_llm = {
            "outlet_id": outlet_id,
            "compliance_score": compliance["compliance_score"],
            "classification": compliance["classification"],
            "risk_level": risk["risk_level"],
            "total_violations": len(violations),
            "severity_distribution": severity_distribution(violations),
        }
        summary = self.llm.explain_findings(facts_for_llm)

        return {
            "intent": "outlet_analysis",
            "status": "success",
            "summary": summary,
            "audit_data": report,
            "compliance_score": compliance["compliance_score"],
            "violations": [v.__dict__ for v in violations],
            "risk_level": risk["risk_level"],
            "risk_reasons": risk["reasons"],
            "insights": risk["reasons"],
            "recommendations": report["recommendations"],
            "proposed_actions": [p.__dict__ for p in proposed],
            "requires_human_approval": len(proposed) > 0,
            "confidence": 0.95 if compliance["unknown_checks"] == 0 else 0.75,
            "warnings": [],
            "data_limitations": data_limitations,
        }

    def analyze_all(self) -> List[Dict[str, Any]]:
        outlets, _, _, _ = self._load()
        return [self.analyze_outlet(oid) for oid in outlets.keys()]

    # ---------- NL query ----------
    def handle_query(self, query: str) -> Dict[str, Any]:
        intent = self.llm.detect_intent(query)
        logger.info(f"Detected intent: {intent}")

        try:
            if intent == "list_outlets_with_compliance_problems":
                return self._q_compliance_problems()
            if intent == "todays_findings":
                return self._q_todays_findings()
            if intent == "most_violations":
                return self._q_most_violations()
            if intent == "critical_violations":
                return self._q_critical_violations()
            if intent == "why_outlet_at_risk":
                return self._q_why_risk(query)
            if intent == "overdue_corrective_actions":
                return self._q_overdue()
            if intent == "generate_audit_report":
                return self._q_report(query)
            if intent == "compare_compliance":
                return self._q_compare()
            if intent == "most_violated_policies":
                return self._q_most_violated_policies()
            if intent == "improving_compliance":
                return self._q_improving()
            if intent == "prepare_corrective_actions":
                return self._q_prepare_actions()
            return self._q_overview()
        except Exception as e:
            logger.exception("Query handling failed")
            return self._error(f"Query failed: {e}", intent=intent)

    # ---------- query handlers ----------
    def _q_overview(self):
        results = self.analyze_all()
        return self._wrap("overview", "Compliance overview for all outlets.",
                          {"outlets": results})

    def _q_compliance_problems(self):
        results = [r for r in self.analyze_all()
                   if r.get("risk_level") in ("HIGH", "CRITICAL")
                   or r.get("compliance_score", 100) < 60]
        return self._wrap("compliance_problems",
                          f"{len(results)} outlet(s) with compliance problems.", {"outlets": results})

    def _q_todays_findings(self):
        results = self.analyze_all()
        all_v = [v for r in results for v in r.get("violations", [])]
        return self._wrap("todays_findings",
                          f"{len(all_v)} finding(s) today.", {"violations": all_v})

    def _q_most_violations(self):
        results = self.analyze_all()
        ranked = sorted(results, key=lambda r: len(r.get("violations", [])), reverse=True)
        top = ranked[0] if ranked else None
        return self._wrap("most_violations",
                          f"Outlet with most violations: {top['audit_data']['outlet']['outlet_id'] if top else 'N/A'}",
                          {"top": top})

    def _q_critical_violations(self):
        results = self.analyze_all()
        crits = [v for r in results for v in r.get("violations", []) if v.get("severity") == "CRITICAL"]
        return self._wrap("critical_violations", f"{len(crits)} critical violation(s).", {"violations": crits})

    def _q_why_risk(self, query: str):
        oid = self._extract_outlet_id(query)
        if not oid:
            return self._error("Could not identify outlet ID in query.")
        result = self.analyze_outlet(oid)
        if result["status"] != "success":
            return result
        return self._wrap("why_risk",
                          f"Outlet {oid} risk reasons: {', '.join(result['risk_reasons'])}",
                          {"outlet_analysis": result})

    def _q_overdue(self):
        _, _, _, actions = self._load()
        overdue = find_overdue_actions(actions)
        return self._wrap("overdue_actions", f"{len(overdue)} overdue corrective action(s).",
                          {"overdue": overdue})

    def _q_report(self, query: str):
        oid = self._extract_outlet_id(query)
        if not oid:
            return self._error("Please specify an outlet ID (e.g., 'report for outlet 104').")
        result = self.analyze_outlet(oid)
        if result["status"] != "success":
            return result
        return self._wrap("audit_report", f"Audit report generated for outlet {oid}.",
                          {"report": result["audit_data"]})

    def _q_compare(self):
        results = self.analyze_all()
        ranked = sorted(results, key=lambda r: r.get("compliance_score", 0), reverse=True)
        return self._wrap("compare_compliance",
                          "Outlets ranked by compliance score.",
                          {"ranking": [
                              {
                                  "outlet_id": r["audit_data"]["outlet"]["outlet_id"],
                                  "score": r["compliance_score"],
                                  "risk": r["risk_level"],
                              } for r in ranked
                          ]})

    def _q_most_violated_policies(self):
        results = self.analyze_all()
        counts: Dict[str, int] = {}
        for r in results:
            for v in r.get("violations", []):
                counts[v["category"]] = counts.get(v["category"], 0) + 1
        ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return self._wrap("most_violated_policies",
                          "Policy categories ranked by violation count.",
                          {"categories": [{"category": c, "count": n} for c, n in ranked]})

    def _q_improving(self):
        # Placeholder — needs historical scores. Return honest limitation.
        return self._wrap("improving_compliance",
                          "Trend detection requires historical compliance scores.",
                          {"note": "Insufficient historical data to determine improving outlets."})

    def _q_prepare_actions(self):
        results = self.analyze_all()
        all_proposed = [p for r in results for p in r.get("proposed_actions", [])]
        return self._wrap("prepare_corrective_actions",
                          f"Prepared {len(all_proposed)} proposed action(s) — PENDING_APPROVAL.",
                          {"proposed_actions": all_proposed, "requires_human_approval": True})

    # ---------- helpers ----------
    def _wrap(self, intent, summary, data):
        return {
            "intent": intent,
            "status": "success",
            "summary": summary,
            "audit_data": data,
            "compliance_score": None,
            "violations": data.get("violations", []),
            "risk_level": None,
            "insights": [],
            "recommendations": [],
            "proposed_action": None,
            "requires_human_approval": intent == "prepare_corrective_actions",
            "confidence": 0.9,
            "warnings": [],
            "data_limitations": [],
        }

    def _error(self, msg: str, intent: str = "error", outlet_id: str | None = None):
        return {
            "intent": intent,
            "status": "error",
            "summary": msg,
            "audit_data": {"outlet_id": outlet_id} if outlet_id else {},
            "compliance_score": None,
            "violations": [],
            "risk_level": None,
            "insights": [],
            "recommendations": [],
            "proposed_action": None,
            "requires_human_approval": False,
            "confidence": 0.0,
            "warnings": [msg],
            "data_limitations": [],
        }

    @staticmethod
    def _extract_outlet_id(query: str) -> Optional[str]:
        import re
        m = re.search(r"\b(\d{3,})\b", query)
        return m.group(1) if m else None