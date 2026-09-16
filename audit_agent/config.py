"""Configuration for the Audit Agent."""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration — use NEW working model names
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
LLM_MODEL = os.getenv("AUDIT_LLM_MODEL", "gemini-2.0-flash")  # was gemini-1.5-flash (deprecated)
LLM_ENABLED = bool(GOOGLE_API_KEY)

# Data paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTLETS_CSV = os.path.join(DATA_DIR, "outlets.csv")
OPERATIONAL_CSV = os.path.join(DATA_DIR, "operational_records.csv")
RULES_JSON = os.path.join(DATA_DIR, "audit_rules.json")
CORRECTIVE_ACTIONS_CSV = os.path.join(DATA_DIR, "corrective_actions.csv")

# Compliance scoring
SEVERITY_WEIGHTS = {
    "LOW": 1.0,
    "MEDIUM": 2.0,
    "HIGH": 3.0,
    "CRITICAL": 5.0,
}

# Score classification thresholds
SCORE_BANDS = [
    (90, "EXCELLENT"),
    (75, "GOOD"),
    (60, "ACCEPTABLE"),
    (45, "AT_RISK"),
    (25, "NON_COMPLIANT"),
    (0,  "CRITICAL"),
]

# Risk thresholds
RISK_THRESHOLDS = {
    "CRITICAL": 75,
    "HIGH": 50,
    "MEDIUM": 25,
    "LOW": 0,
}