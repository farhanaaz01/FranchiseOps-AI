"""CSV / JSON / in-memory provider — creates sample data if missing."""
import csv
import json
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from audit_agent.config import (
    DATA_DIR, OUTLETS_CSV, OPERATIONAL_CSV, RULES_JSON, CORRECTIVE_ACTIONS_CSV
)
from audit_agent.data_access.base_provider import BaseDataProvider

logger = logging.getLogger(__name__)


class DataProvider(BaseDataProvider):
    def __init__(self, auto_seed: bool = True):
        os.makedirs(DATA_DIR, exist_ok=True)
        if auto_seed:
            self._seed_if_missing()

    # ---------- seed ----------
    def _seed_if_missing(self):
        if not os.path.exists(OUTLETS_CSV):
            self._write_csv(OUTLETS_CSV, self._sample_outlets())
            logger.info(f"Seeded {OUTLETS_CSV}")
        if not os.path.exists(OPERATIONAL_CSV):
            self._write_csv(OPERATIONAL_CSV, self._sample_operational())
            logger.info(f"Seeded {OPERATIONAL_CSV}")
        if not os.path.exists(RULES_JSON):
            with open(RULES_JSON, "w", encoding="utf-8") as f:
                json.dump(self._sample_rules(), f, indent=2)
            logger.info(f"Seeded {RULES_JSON}")
        if not os.path.exists(CORRECTIVE_ACTIONS_CSV):
            self._write_csv(CORRECTIVE_ACTIONS_CSV, self._sample_corrective())
            logger.info(f"Seeded {CORRECTIVE_ACTIONS_CSV}")

    @staticmethod
    def _write_csv(path: str, rows: List[Dict[str, Any]]):
        if not rows:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    # ---------- public API ----------
    def get_outlets(self) -> List[Dict[str, Any]]:
        return self._read_csv(OUTLETS_CSV)

    def get_operational_records(self) -> List[Dict[str, Any]]:
        return self._read_csv(OPERATIONAL_CSV)

    def get_audit_rules(self) -> List[Dict[str, Any]]:
        try:
            with open(RULES_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read rules: {e}")
            return []

    def get_corrective_actions(self) -> List[Dict[str, Any]]:
        return self._read_csv(CORRECTIVE_ACTIONS_CSV)

    # ---------- helpers ----------
    @staticmethod
    def _read_csv(path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            logger.warning(f"Missing file: {path}")
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return [dict(r) for r in csv.DictReader(f)]
        except Exception as e:
            logger.error(f"CSV read failed for {path}: {e}")
            return []

    # ---------- sample data ----------
    @staticmethod
    def _sample_outlets():
        return [
            {"outlet_id": "101", "name": "Downtown Bistro", "location": "NYC", "franchise_id": "F001", "status": "ACTIVE"},
            {"outlet_id": "102", "name": "Uptown Grill",    "location": "NYC", "franchise_id": "F001", "status": "ACTIVE"},
            {"outlet_id": "103", "name": "Brooklyn Cafe",   "location": "BKN", "franchise_id": "F002", "status": "ACTIVE"},
            {"outlet_id": "104", "name": "Queens Kitchen",  "location": "QNS", "franchise_id": "F002", "status": "ACTIVE"},
        ]

    @staticmethod
    def _sample_operational():
        today = datetime.utcnow().date()
        rows = []
        # Outlet 101 — mostly compliant
        for d in range(7):
            rows.append({
                "record_id": f"R101-{d}", "outlet_id": "101", "date": str(today - timedelta(days=d)),
                "cleaning_done": "true", "hygiene_check": "true", "food_safety_check": "true",
                "staff_uniform": "true", "safety_inspection": "true", "equipment_check": "true",
                "required_docs": "true",
            })
        # Outlet 102 — repeated issues
        for d in range(7):
            rows.append({
                "record_id": f"R102-{d}", "outlet_id": "102", "date": str(today - timedelta(days=d)),
                "cleaning_done": "false" if d % 2 == 0 else "true",
                "hygiene_check": "false" if d < 3 else "true",
                "food_safety_check": "true", "staff_uniform": "true",
                "safety_inspection": "false" if d == 0 else "true",
                "equipment_check": "true", "required_docs": "true",
            })
        # Outlet 103 — clean
        for d in range(7):
            rows.append({
                "record_id": f"R103-{d}", "outlet_id": "103", "date": str(today - timedelta(days=d)),
                "cleaning_done": "true", "hygiene_check": "true", "food_safety_check": "true",
                "staff_uniform": "true", "safety_inspection": "true", "equipment_check": "true",
                "required_docs": "true",
            })
        # Outlet 104 — critical
        for d in range(7):
            rows.append({
                "record_id": f"R104-{d}", "outlet_id": "104", "date": str(today - timedelta(days=d)),
                "cleaning_done": "false", "hygiene_check": "false",
                "food_safety_check": "false" if d < 4 else "true",
                "staff_uniform": "true", "safety_inspection": "false",
                "equipment_check": "false" if d < 2 else "true",
                "required_docs": "false",
            })
        return rows

    @staticmethod
    def _sample_rules():
        return [
            {"rule_id": "RULE001", "name": "Daily Cleaning",       "description": "Cleaning must be done daily",         "category": "HYGIENE",    "field": "cleaning_done",       "expected": True, "operator": "eq", "severity": "HIGH",     "weight": 3.0},
            {"rule_id": "RULE002", "name": "Hygiene Check",        "description": "Hygiene check must pass",             "category": "HYGIENE",    "field": "hygiene_check",       "expected": True, "operator": "eq", "severity": "CRITICAL", "weight": 5.0},
            {"rule_id": "RULE003", "name": "Food Safety Check",    "description": "Food safety check must pass",         "category": "FOOD_SAFETY","field": "food_safety_check",   "expected": True, "operator": "eq", "severity": "CRITICAL", "weight": 5.0},
            {"rule_id": "RULE004", "name": "Staff Uniform",        "description": "Staff must wear uniform",             "category": "STAFF",      "field": "staff_uniform",       "expected": True, "operator": "eq", "severity": "LOW",      "weight": 1.0},
            {"rule_id": "RULE005", "name": "Safety Inspection",    "description": "Safety inspection must be recorded",  "category": "SAFETY",     "field": "safety_inspection",   "expected": True, "operator": "eq", "severity": "HIGH",     "weight": 3.0},
            {"rule_id": "RULE006", "name": "Equipment Check",      "description": "Equipment must be checked",           "category": "EQUIPMENT",  "field": "equipment_check",     "expected": True, "operator": "eq", "severity": "MEDIUM",   "weight": 2.0},
            {"rule_id": "RULE007", "name": "Required Docs",        "description": "Required documentation available",    "category": "DOCUMENTS",  "field": "required_docs",       "expected": True, "operator": "eq", "severity": "HIGH",     "weight": 3.0},
        ]

    @staticmethod
    def _sample_corrective():
        return [
            {"action_id": "CA001", "violation_id": "V-102-OLD", "outlet_id": "102",
             "recommended_action": "Re-train staff on cleaning schedule",
             "priority": "HIGH", "status": "OVERDUE", "due_date": "2026-01-01",
             "completed_date": "", "requires_human_approval": "true", "assigned_to": "Mgr-102", "verified": "false"},
        ]