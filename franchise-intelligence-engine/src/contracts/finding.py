"""Standardized agent finding contract."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional
import uuid


VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"}
VALID_TRENDS = {"IMPROVING", "STABLE", "DECLINING", "UNKNOWN"}
VALID_FINDING_TYPES = {"FACT", "ANOMALY", "TREND", "ALERT", "OPPORTUNITY", "UNKNOWN"}

KNOWN_AGENTS = {
    "Outlet Performance Agent",
    "Inventory Agent",
    "Staff Agent",
    "Marketing Agent",
    "Audit Agent",
}


@dataclass
class Finding:
    agent_name: str
    finding_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    outlet_id: Optional[str] = None
    category: str = "general"
    metric: str = "unknown"
    value: Any = None
    baseline: Any = None
    severity: str = "UNKNOWN"
    trend: str = "UNKNOWN"
    finding_type: str = "UNKNOWN"
    description: str = ""
    evidence: list = field(default_factory=list)
    confidence: float = 0.5
    timestamp: Optional[str] = None
    recommendation: Optional[str] = None
    requires_human_approval: bool = False

    def __post_init__(self):
        # Normalize severity/trend/type
        self.severity = str(self.severity).upper() if self.severity else "UNKNOWN"
        if self.severity not in VALID_SEVERITIES:
            self.severity = "UNKNOWN"

        self.trend = str(self.trend).upper() if self.trend else "UNKNOWN"
        if self.trend not in VALID_TRENDS:
            self.trend = "UNKNOWN"

        self.finding_type = str(self.finding_type).upper() if self.finding_type else "UNKNOWN"
        if self.finding_type not in VALID_FINDING_TYPES:
            self.finding_type = "UNKNOWN"

        # Clamp confidence
        try:
            self.confidence = float(self.confidence)
        except (TypeError, ValueError):
            self.confidence = 0.5
        self.confidence = max(0.0, min(1.0, self.confidence))

        # Timestamp default
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

        # Ensure evidence is a list
        if self.evidence is None:
            self.evidence = []
        if not isinstance(self.evidence, list):
            self.evidence = [self.evidence]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Finding":
        # Ignore unknown fields gracefully
        valid_fields = {f for f in cls.__dataclass_fields__}
        clean = {k: v for k, v in data.items() if k in valid_fields}
        if "agent_name" not in clean:
            clean["agent_name"] = "Unknown Agent"
        return cls(**clean)