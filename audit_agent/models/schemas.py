"""Pydantic-free schemas for portability (plain dataclasses)."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Outlet:
    outlet_id: str
    name: str = ""
    location: str = ""
    franchise_id: str = ""
    status: str = "ACTIVE"


@dataclass
class AuditRule:
    rule_id: str
    name: str
    description: str = ""
    category: str = "GENERAL"
    field: str = ""              # operational field to check
    expected: Any = True         # expected value/condition
    operator: str = "eq"         # eq, ne, gte, lte, contains
    severity: str = "MEDIUM"
    weight: float = 1.0


@dataclass
class Violation:
    violation_id: str
    outlet_id: str
    rule_id: str
    category: str
    description: str
    severity: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    detected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    recommended_action: str = ""
    status: str = "OPEN"


@dataclass
class CorrectiveAction:
    action_id: str
    violation_id: str
    outlet_id: str
    recommended_action: str
    priority: str = "MEDIUM"
    status: str = "PENDING"
    due_date: Optional[str] = None
    completed_date: Optional[str] = None
    requires_human_approval: bool = True
    assigned_to: Optional[str] = None
    verified: bool = False


@dataclass
class ProposedAction:
    action_id: str
    action_type: str
    outlet_id: str
    reason: str
    evidence: Dict[str, Any]
    recommended_action: str
    priority: str
    estimated_cost: Optional[float] = None
    status: str = "PENDING_APPROVAL"
    requires_human_approval: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None