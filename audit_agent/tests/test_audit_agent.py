"""Automated tests for the Audit Agent."""
import unittest

from audit_agent.data_access.data_provider import DataProvider
from audit_agent.agents.audit_agent import AuditAgent
from audit_agent.agents.compliance_engine import evaluate_check, calculate_compliance_score, classify_score
from audit_agent.agents.violation_detector import detect_violations
from audit_agent.agents.risk_analyzer import calculate_risk
from audit_agent.agents.corrective_action_tracker import find_overdue_actions
from audit_agent.models.schemas import ProposedAction, Violation
from audit_agent.utils.llm_interface import LLMInterface


class TestComplianceEngine(unittest.TestCase):
    def test_evaluate_unknown(self):
        self.assertEqual(evaluate_check({}, {"field": "x", "expected": True}), "UNKNOWN")

    def test_evaluate_non_compliant(self):
        self.assertEqual(
            evaluate_check({"cleaning_done": "false"}, {"field": "cleaning_done", "expected": True, "operator": "eq"}),
            "NON_COMPLIANT",
        )

    def test_score_calculation(self):
        records = [{"cleaning_done": "true"}, {"cleaning_done": "false"}]
        rules = [{"field": "cleaning_done", "expected": True, "operator": "eq",
                  "weight": 3.0, "severity": "HIGH", "rule_id": "R1", "name": "Cleaning", "category": "HYGIENE"}]
        result = calculate_compliance_score(records, rules)
        self.assertEqual(result["compliance_score"], 50.0)

    def test_classify(self):
        self.assertEqual(classify_score(95), "EXCELLENT")
        self.assertEqual(classify_score(10), "CRITICAL")


class TestViolationDetector(unittest.TestCase):
    def test_detect(self):
        records = [{"cleaning_done": "false", "date": "2026-01-01", "record_id": "X"}]
        rules = [{"field": "cleaning_done", "expected": True, "operator": "eq",
                  "weight": 3.0, "severity": "HIGH", "rule_id": "R1", "name": "Cleaning", "category": "HYGIENE"}]
        v = detect_violations("101", records, rules)
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0].severity, "HIGH")


class TestRiskAnalyzer(unittest.TestCase):
    def test_critical_violations_raise_risk(self):
        v = [Violation("V1", "104", "R1", "HYGIENE", "x", "CRITICAL")]
        r = calculate_risk("104", v, compliance_score=40.0, previous_score=None, overdue_actions=0)
        self.assertIn(r["risk_level"], ("HIGH", "CRITICAL"))


class TestOverdue(unittest.TestCase):
    def test_overdue(self):
        actions = [{"action_id": "1", "status": "PENDING", "due_date": "2000-01-01"}]
        self.assertEqual(len(find_overdue_actions(actions)), 1)


class TestHumanInTheLoop(unittest.TestCase):
    def test_unapproved_action_blocked(self):
        agent = AuditAgent(provider=DataProvider(auto_seed=True), llm=LLMInterface())
        action = ProposedAction(
            action_id="PA-X", action_type="TEST", outlet_id="104",
            reason="test", evidence={}, recommended_action="x", priority="CRITICAL",
        )
        result = agent.executor.execute(action)
        self.assertFalse(result["executed"])

    def test_approved_action_executes(self):
        agent = AuditAgent(provider=DataProvider(auto_seed=True), llm=LLMInterface())
        action = ProposedAction(
            action_id="PA-Y", action_type="TEST", outlet_id="104",
            reason="test", evidence={}, recommended_action="x", priority="CRITICAL",
        )
        agent.executor.approve(action, approver="HumanHead")
        result = agent.executor.execute(action)
        self.assertTrue(result["executed"])


class TestAgentQueries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = AuditAgent(provider=DataProvider(auto_seed=True), llm=LLMInterface())

    def test_overview(self):
        r = self.agent.handle_query("compliance overview")
        self.assertEqual(r["status"], "success")

    def test_unknown_outlet(self):
        r = self.agent.analyze_outlet("999")
        self.assertEqual(r["status"], "error")

    def test_report(self):
        r = self.agent.handle_query("generate an audit report for outlet 104")
        self.assertEqual(r["status"], "success")


if __name__ == "__main__":
    unittest.main()