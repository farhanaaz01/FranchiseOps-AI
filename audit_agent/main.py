"""Standalone demonstration of the Audit Agent."""
import json
import logging
import sys

from audit_agent.data_access.data_provider import DataProvider
from audit_agent.agents.audit_agent import AuditAgent
from audit_agent.utils.llm_interface import LLMInterface

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def pp(obj):
    print(json.dumps(obj, indent=2, default=str))


def demo():
    print("=" * 80)
    print(" AUDIT AGENT - STANDALONE DEMONSTRATION")
    print("=" * 80)

    provider = DataProvider(auto_seed=True)
    llm = LLMInterface()
    print(f"LLM enabled: {llm.enabled} (model: {llm.model_name})")
    print("=" * 80)

    agent = AuditAgent(provider=provider, llm=llm)

    # TEST 1
    print("\n[TEST 1: Full compliance overview]")
    pp(agent.handle_query("show me a compliance overview"))

    # TEST 2
    print("\n[TEST 2: Outlets with compliance problems]")
    pp(agent.handle_query("which outlets have compliance problems?"))

    # TEST 3
    print("\n[TEST 3: Critical violations]")
    pp(agent.handle_query("what are the critical violations?"))

    # TEST 4
    print("\n[TEST 4: Why is outlet 104 at risk?]")
    pp(agent.handle_query("why is outlet 104 at risk?"))

    # TEST 5
    print("\n[TEST 5: Audit report for outlet 104]")
    pp(agent.handle_query("generate an audit report for outlet 104"))

    # TEST 6
    print("\n[TEST 6: Overdue corrective actions]")
    pp(agent.handle_query("show overdue corrective actions"))

    # TEST 7
    print("\n[TEST 7: Prepare corrective actions for critical violations]")
    res = agent.handle_query("prepare corrective actions for the critical violations")
    pp(res)

    # TEST 8 — human-in-the-loop enforcement
    print("\n[TEST 8: Unauthorized execution prevention]")
    proposed = res.get("audit_data", {}).get("proposed_actions", [])
    if proposed:
        from audit_agent.models.schemas import ProposedAction
        pa = ProposedAction(**proposed[0])
        attempt = agent.executor.execute(pa)
        pp(attempt)
        assert attempt["executed"] is False, "SECURITY FAILURE: action executed without approval!"
        print("✅ Confirmed: agent CANNOT execute without human approval.")
    else:
        print("No proposed actions to test.")

    # TEST 9 — approval then execution
    print("\n[TEST 9: Human approval unlocks execution]")
    if proposed:
        from audit_agent.models.schemas import ProposedAction
        pa = ProposedAction(**proposed[0])
        agent.executor.approve(pa, approver="HumanHead-Alice")
        result = agent.executor.execute(pa)
        pp(result)
        assert result["executed"] is True
        print("✅ Confirmed: approved action can be executed by executor.")

    print("\n" + "=" * 80)
    print(" DEMONSTRATION COMPLETE")
    print("=" * 80)


def interactive():
    provider = DataProvider(auto_seed=True)
    agent = AuditAgent(provider=provider)
    print("Audit Agent interactive mode. Type 'exit' to quit.")
    while True:
        try:
            q = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("exit", "quit"):
            break
        pp(agent.handle_query(q))


if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "1"
    if choice == "2":
        interactive()
    else:
        demo()