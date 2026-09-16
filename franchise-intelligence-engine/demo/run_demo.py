"""Standalone demo — no backend required."""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.providers.mock_provider import MockProvider
from src.engine.config import load_config
from src.engine.orchestrator import FranchiseIntelligenceEngine
import json


def main():
    print("=" * 70)
    print("FRANCHISEOPS AI — FRANCHISE INTELLIGENCE ENGINE DEMO")
    print("=" * 70)

    config = load_config("config.yaml")
    provider = MockProvider()
    engine = FranchiseIntelligenceEngine(provider, config, use_llm=True)

    queries = [
        "How is the franchise performing?",
        "Which outlets are at risk?",
        "What are the top strategic recommendations?",
        "Where are our biggest growth opportunities?",
    ]

    for q in queries:
        print(f"\n>>> QUERY: {q}")
        result = engine.run(q)
        print(f"Intent: {result['intent']}")
        print(f"Health: {result['franchise_health_score']} ({result['health_status']})")
        print(f"Risks: {len(result['risks'])}  Opportunities: {len(result['opportunities'])}")
        print(f"Proposed actions: {len(result['proposed_actions'])} "
              f"| requires_human_approval={result['requires_human_approval']}")
        if result["proposed_actions"]:
            for a in result["proposed_actions"]:
                print(f"   • {a['action_id']} [{a['status']}] executed={a['executed']}")
        if result["warnings"]:
            print(f"   Warnings: {result['warnings']}")

    # Detailed dump of first query
    full = engine.run("How is the franchise performing?")
    print("\n" + "=" * 70)
    print("FULL STRUCTURED OUTPUT (query 1)")
    print("=" * 70)
    print(json.dumps(full, indent=2, default=str))


if __name__ == "__main__":
    main()