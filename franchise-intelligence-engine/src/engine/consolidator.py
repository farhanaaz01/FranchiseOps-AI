"""Consolidates findings across agents; detects duplicates, conflicts, staleness."""
from __future__ import annotations
from datetime import datetime, timezone
from collections import defaultdict
from typing import List, Dict, Any
from src.contracts.finding import Finding


class Consolidator:
    def __init__(self, config: dict):
        self.config = config

    def consolidate(self, findings: List[Finding]) -> Dict[str, Any]:
        by_agent = defaultdict(list)
        by_outlet = defaultdict(list)
        by_category = defaultdict(list)

        seen_keys = set()
        duplicates = []
        clean_findings = []

        for f in findings:
            key = (f.agent_name, f.outlet_id, f.metric, str(f.value))
            if key in seen_keys:
                duplicates.append(f)
                continue
            seen_keys.add(key)
            clean_findings.append(f)
            by_agent[f.agent_name].append(f)
            if f.outlet_id:
                by_outlet[f.outlet_id].append(f)
            by_category[f.category].append(f)

        conflicts = self._detect_conflicts(clean_findings)
        stale = self._detect_stale(clean_findings)

        return {
            "findings": clean_findings,
            "by_agent": dict(by_agent),
            "by_outlet": dict(by_outlet),
            "by_category": dict(by_category),
            "duplicates": duplicates,
            "conflicts": conflicts,
            "stale": stale,
            "total_findings": len(clean_findings),
            "agents_reported": sorted(by_agent.keys()),
        }

    def _detect_conflicts(self, findings: List[Finding]) -> List[dict]:
        """Same outlet+metric with different values from same agent."""
        groups = defaultdict(list)
        for f in findings:
            groups[(f.agent_name, f.outlet_id, f.metric)].append(f)
        conflicts = []
        for key, items in groups.items():
            values = {str(i.value) for i in items}
            if len(values) > 1:
                conflicts.append({
                    "key": key,
                    "values": list(values),
                    "count": len(items),
                    "note": "Conflicting values detected — flag for review.",
                })
        return conflicts

    def _detect_stale(self, findings: List[Finding]) -> List[Finding]:
        freshness = self.config.get("data_freshness_days", 7)
        now = datetime.now(timezone.utc)
        stale = []
        for f in findings:
            if not f.timestamp:
                stale.append(f)
                continue
            try:
                ts = datetime.fromisoformat(f.timestamp.replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if (now - ts).days > freshness:
                    stale.append(f)
            except Exception:
                stale.append(f)
        return stale