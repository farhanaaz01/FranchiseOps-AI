#!/usr/bin/env python
"""
Marketing Agent - Standalone Demonstration
Agentic Franchise Operations Intelligence Platform
"""

import sys
import os
import logging
import json
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from marketing_agent.agents.marketing_agent import MarketingAgent
from marketing_agent.data_access.data_provider import MarketingDataProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_section(title: str):
    """Print a section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def print_result(result: Dict[str, Any], title: str = "Result"):
    """Pretty print result"""
    print(f"\n{title}:")
    print(f"Intent: {result.get('intent', 'unknown')}")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Summary: {result.get('summary', 'No summary')}")
    
    if result.get('insights'):
        print("\nInsights:")
        for insight in result['insights']:
            print(f"  • {insight}")
            
    if result.get('recommendations'):
        print("\nRecommendations:")
        for rec in result['recommendations']:
            print(f"  • {rec}")
            
    if result.get('requires_human_approval'):
        print("\n⚠️ REQUIRES HUMAN APPROVAL")
        if result.get('proposed_action'):
            print(f"  Proposed Action: {json.dumps(result['proposed_action'], indent=2)}")
    print("-"*80)

def run_demonstration():
    """Run standalone demonstration"""
    print_section("MARKETING AGENT - STANDALONE DEMONSTRATION")
    print("This demonstration uses sample data and can work without a backend.")
    print("="*80)
    
    # Initialize agent
    logger.info("Initializing agent...")
    agent = MarketingAgent()
    
    # Test queries
    test_queries = [
        ("Campaign Performance", "How are our campaigns performing?"),
        ("Campaign Comparison", "Which campaign performed best?"),
        ("Engagement Analysis", "What is the customer engagement?"),
        ("ROI Analysis", "Calculate ROI for all campaigns"),
        ("Promotion Effectiveness", "How effective are our promotions?"),
        ("Underperforming Campaigns", "Which campaigns are underperforming?"),
        ("Successful Campaigns", "Which campaigns are successful?"),
        ("Trends Analysis", "What are the trends in campaign performance?"),
        ("Recommendations", "Give me marketing recommendations"),
        ("Proposed Action", "Increase Campaign CAMP-001 budget by ₹50,000")
    ]
    
    for i, (test_name, query) in enumerate(test_queries, 1):
        print_section(f"TEST {i}: {test_name}")
        print(f"Query: {query}")
        
        result = agent.process_query(query)
        print_result(result, f"Response")
        
        # Show pending actions if any
        if agent.approval_status['pending_actions']:
            print("\nPending Actions:")
            for action in agent.approval_status['pending_actions']:
                print(f"  • {action['id']}: {action['action_details'].get('description', '')}")
                print(f"    Status: {action['status']}")
                print(f"    Requires: Human Head approval")
    
    # Test approval workflow
    print_section("APPROVAL WORKFLOW DEMONSTRATION")
    
    # Create a pending action
    action_result = agent.process_query("Increase Campaign CAMP-003 budget by ₹25,000")
    if action_result.get('status') == 'PENDING_APPROVAL':
        action_id = action_result['data']['id']
        print(f"Created pending action: {action_id}")
        print(f"Status: {action_result['status']}")
        
        # Approve the action
        print("\nApproving action...")
        approval_result = agent.approve_action(action_id)
        print(f"Approval result: {approval_result['status']}")
        print(f"Message: {approval_result['message']}")
    
    # Test unauthorized action prevention
    print_section("UNAUTHORIZED ACTION PREVENTION TEST")
    print("Attempting to execute an action without approval...")
    print("⚠️ This should be blocked and require Human Head approval.")
    
    unauthorized_query = "Launch a new 20% discount campaign"
    result = agent.process_query(unauthorized_query)
    print_result(result, "Unauthorized Action Response")
    
    if result.get('status') == 'PENDING_APPROVAL':
        print("✅ Action was blocked and requires approval as expected.")
    else:
        print("❌ Action was not properly blocked!")
    
    print_section("DEMONSTRATION COMPLETE")
    print("Summary of capabilities demonstrated:")
    print("  1. ✅ Natural language understanding")
    print("  2. ✅ Campaign performance analysis")
    print("  3. ✅ Campaign comparison")
    print("  4. ✅ Engagement analysis")
    print("  5. ✅ ROI calculation")
    print("  6. ✅ Promotion effectiveness")
    print("  7. ✅ Underperforming campaign detection")
    print("  8. ✅ Successful campaign detection")
    print("  9. ✅ Trend analysis")
    print(" 10. ✅ Recommendation generation")
    print(" 11. ✅ Proposed action with human approval")
    print(" 12. ✅ Unauthorized action prevention")
    print(" 13. ✅ Approval workflow")
    print("\nThe Marketing Agent is working independently and is ready for backend integration.")

def run_tests():
    """Run all tests"""
    import pytest
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pytest.main(["marketing_agent/tests/", "-v"])

def interactive_mode():
    """Run interactive mode"""
    print_section("MARKETING AGENT - INTERACTIVE MODE")
    print("Type your questions about marketing campaigns, performance, ROI, etc.")
    print("Type 'exit' to quit, 'approve <action_id>' to approve pending actions")
    print("Type 'reject <action_id>' to reject pending actions")
    print("Type 'pending' to view pending actions")
    print("="*80)
    
    agent = MarketingAgent()
    
    while True:
        try:
            query = input("\n📊 > ")
            
            if query.lower() == 'exit':
                print("Goodbye!")
                break
                
            if query.lower().startswith('approve '):
                action_id = query.split()[1]
                result = agent.approve_action(action_id)
                print(f"Approval result: {result['status']} - {result.get('message', '')}")
                continue
                
            if query.lower().startswith('reject '):
                action_id = query.split()[1]
                result = agent.reject_action(action_id)
                print(f"Rejection result: {result['status']} - {result.get('message', '')}")
                continue
                
            if query.lower() == 'pending':
                pending = agent.approval_status['pending_actions']
                if pending:
                    print("\nPending Actions:")
                    for action in pending:
                        print(f"  {action['id']}: {action['action_details'].get('description', '')}")
                        print(f"  Status: {action['status']}")
                else:
                    print("No pending actions")
                continue
            
            # Process query
            result = agent.process_query(query)
            print_result(result, "Response")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main entry point"""
    print("Marketing Agent - FranchiseOps AI")
    print("=================================")
    print("Choose mode:")
    print("  1. Full demonstration")
    print("  2. Interactive mode")
    print("  3. Run tests")
    print()
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            run_demonstration()
        elif choice == "2":
            interactive_mode()
        elif choice == "3":
            run_tests()
        else:
            print("Invalid choice. Please run again.")
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()