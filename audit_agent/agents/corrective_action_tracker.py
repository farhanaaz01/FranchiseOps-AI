"""Corrective-action tracking + overdue detection + proposed action creation."""
from datetime import datetime
from typing import List, Dict, Any

from audit_agent.models.schemas import Violation, CorrectiveAction, ProposedAction


def build_corrective_actions(violations: List[Violation]) -> List[CorrectiveAction]:
    actions = []
    for i, v in enumerate(violations, 1):
        actions.append(CorrectiveAction(
            action_id=f"CA-{v.outlet_id}-{i:03d}",
            violation_id=v.violation_id,
            outlet_id=v.outlet_id,
            recommended_action=v.recommended_action,
            priority=v.severity,
            status="PENDING",
            requires_human_approval=True,
        ))
    return actions


def find_overdue_actions(actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    overdue = []
    today = datetime.utcnow().date()
    for a in actions:
        status = str(a.get("status", "")).upper()
        due = a.get("due_date", "")
        if status in ("COMPLETED", "VERIFIED", "CANCELLED"):
            continue
        if not due:
            continue
        try:
            due_d = datetime.strptime(due, "%Y-%m-%d").date()
            if due_d < today:
                overdue.append(a)
        except ValueError:
            continue
    return overdue


def build_proposed_actions(violations: List[Violation]) -> List[ProposedAction]:
    """Consequential actions → PENDING_APPROVAL. NEVER auto-approved."""
    proposed = []
    for i, v in enumerate(violations, 1):
        if v.severity in ("HIGH", "CRITICAL"):
            proposed.append(ProposedAction(
                action_id=f"PA-{v.outlet_id}-{i:03d}",
                action_type="CORRECTIVE_ACTION",
                outlet_id=v.outlet_id,
                reason=v.description,
                evidence=v.evidence,
                recommended_action=v.recommended_action,
                priority=v.severity,
                estimated_cost=None,
                status="PENDING_APPROVAL",
                requires_human_approval=True,
            ))
    return proposed


class ActionExecutor:
    """
    Execution gateway. Only executes actions that have been APPROVED by a human.
    """
    def __init__(self):
        self.log: List[Dict[str, Any]] = []

    def execute(self, action: ProposedAction, approver: str | None = None) -> Dict[str, Any]:
        if action.status != "APPROVED" or not action.approved_by:
            return {
                "executed": False,
                "reason": "BLOCKED: action requires human approval (status must be APPROVED).",
                "action_id": action.action_id,
            }
        self.log.append({"action_id": action.action_id, "approver": action.approved_by})
        return {"executed": True, "action_id": action.action_id}

    def approve(self, action: ProposedAction, approver: str) -> ProposedAction:
        """Only callable by a human/external authority — not by the agent itself."""
        if not approver:
            raise ValueError("Approver identity required.")
        action.status = "APPROVED"
        action.approved_by = approver
        action.approved_at = datetime.utcnow().isoformat()
        return action