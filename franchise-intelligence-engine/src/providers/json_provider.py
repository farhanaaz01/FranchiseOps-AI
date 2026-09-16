"""Provider that reads findings from a JSON file (future integration)."""
import json
from pathlib import Path
from typing import List
from src.contracts.finding import Finding
from src.providers.base import FindingProvider


class JsonProvider(FindingProvider):
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def _load(self, key: str) -> List[Finding]:
        if not self.file_path.exists():
            return []
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WARN] Could not parse {self.file_path}: {e}")
            return []
        return [Finding.from_dict(item) for item in data.get(key, [])]

    def get_outlet_performance_findings(self): return self._load("outlet_performance")
    def get_inventory_findings(self): return self._load("inventory")
    def get_staff_findings(self): return self._load("staff")
    def get_marketing_findings(self): return self._load("marketing")
    def get_audit_findings(self): return self._load("audit")
    def get_historical_franchise_findings(self): return self._load("historical")