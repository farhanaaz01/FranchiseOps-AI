"""Data quality checks."""
from __future__ import annotations
from typing import List, Dict, Any
from src.contracts.finding import Finding


class DataQualityChecker:
    def check(self, findings: List[Finding],
              duplicates: List[Finding],
              conflicts: List[dict],
              stale: List[Finding]) -> Dict[str, Any]:
        issues = []
        invalid = [f for f in findings if f.value is None and f.finding_type != "OPPORTUNITY"]
        if duplicates:
            issues.append(f"{len(duplicates)} duplicate findings detected.")
        if conflicts:
            issues.append(f"{len(conflicts)} conflicting findings flagged for review.")
        if stale:
            issues.append(f"{len(stale)} stale findings (older than freshness window).")
        if invalid:
            issues.append(f"{len(invalid)} findings missing value.")

        missing_agents = [
            a for a in ("Outlet Performance Agent", "Inventory Agent",
                        "Staff Agent", "Marketing Agent", "Audit Agent")
            if a not in {f.agent_name for f in findings}
        ]
        if missing_agents:
            issues.append(f"Agents with no data: {', '.join(missing_agents)}.")

        return {
            "issues": issues,
            "duplicates_count": len(duplicates),
            "conflicts_count": len(conflicts),
            "stale_count": len(stale),
            "invalid_count": len(invalid),
            "missing_agents": missing_agents,
        }