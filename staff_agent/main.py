#!/usr/bin/env python3
"""
Staff Agent - Standalone Demonstration

This is the complete Staff Agent for the FRANCHISEOPS AI platform.
It works independently without requiring the team's backend/database.
"""

import sys
import os
import logging
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from staff_agent.agents.staff_agent import StaffAgent
from staff_agent.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def print_response(response):
    """Pretty print agent response"""
    print(f"\nIntent: {response.get('intent', 'unknown')}")
    print(f"Status: {response.get('status', 'unknown')}")
    
    if response.get('error'):
        print(f"Error: {response['error']}")
        return
    
    print(f"Summary: {response.get('summary', 'No summary')}")
    
    if response.get('data'):
        print("\nData:")
        print(json.dumps(response['data'], indent=2, default=str))
    
    if response.get('insights'):
        print("\nInsights:")
        for insight in response['insights']:
            print(f"  • {insight}")
    
    if response.get('recommendations'):
        print("\nRecommendations:")
        for rec in response['recommendations']:
            approval = "🔒 Requires Approval" if rec.get('requires_approval', False) else "✅ No Approval Needed"
            print(f"  • {rec['finding']}")
            print(f"    → {rec['recommendation']} ({approval})")
    
    if response.get('requires_approval', False):
        print("\n⚠️  This action requires Human Head approval!")
        print(f"   {response.get('message', 'Approval is required.')}")
    
    if response.get('status') == 'PENDING_APPROVAL':
        print("\n📋 ACTION PENDING APPROVAL")
        print("   Use agent.approve_action(action_id) or agent.reject_action(action_id)")

def run_demonstration():
    """Run the full demonstration"""
    print_section("STAFF AGENT - STANDALONE DEMONSTRATION")
    print("This demonstration uses sample data and works without a backend.")
    print(f"LLM Provider: {'Gemini' if Config.USE_LLM else 'Fallback (no LLM)'}")
    print("=" * 80)
    
    # Initialize agent
    logger.info("Initializing agent...")
    agent = StaffAgent(api_key=Config.GOOGLE_API_KEY if Config.USE_LLM else None)
    
    # Test queries
    test_queries = [
        {
            "name": "General Workforce Overview",
            "query": "How is my workforce doing?"
        },
        {
            "name": "Attendance Analysis",
            "query": "What's the attendance rate?"
        },
        {
            "name": "Productivity Analysis",
            "query": "How is staff productivity?"
        },
        {
            "name": "Staffing Shortage Detection",
            "query": "Are there any staffing shortages?"
        },
        {
            "name": "Overtime Analysis",
            "query": "Show me overtime trends."
        },
        {
            "name": "Anomaly Detection",
            "query": "Are there any workforce anomalies?"
        },
        {
            "name": "Staffing Forecast",
            "query": "What's the staffing forecast for next week?"
        },
        {
            "name": "Specific Staff Query",
            "query": "How is staff S001 performing?"
        },
        {
            "name": "Proposed Action (Requires Approval)",
            "query": "Add two employees to evening shift."
        }
    ]
    
    # Store actions for approval demo
    pending_action_ids = []
    
    for test in test_queries:
        print_section(f"TEST: {test['name']}")
        print(f"Query: {test['query']}")
        
        response = agent.process_query(test['query'])
        print_response(response)
        
        # Store action ID if pending
        if response.get('status') == 'PENDING_APPROVAL' and agent.pending_actions:
            pending_action_ids.append(agent.pending_actions[-1]['id'])
    
    # Test unauthorized action prevention
    print_section("TEST: Unauthorized Action Prevention")
    print("Attempting to execute an action without approval...")
    
    response = agent.process_query("Fire employee S001")
    print_response(response)
    
    # Test approval workflow
    if pending_action_ids:
        print_section("TEST: Approval Workflow")
        
        # Show pending actions
        print("\nPending actions:")
        pending = agent.get_pending_actions()
        for action in pending:
            print(f"  {action['id']}: {action['query']} ({action['status']})")
        
        # Approve first action
        if pending:
            action_id = pending[0]['id']
            print(f"\nApproving action {action_id}...")
            result = agent.approve_action(action_id)
            print(f"Result: {result.get('status')}")
            print(f"Message: {result.get('message')}")
            
            # Show remaining pending
            print("\nRemaining pending actions:")
            for action in agent.get_pending_actions():
                print(f"  {action['id']}: {action['query']} ({action['status']})")
    
    # Summary
    print_section("DEMONSTRATION COMPLETE")
    print("Summary of capabilities demonstrated:")
    print("  1. ✅ Natural language understanding")
    print("  2. ✅ Attendance analysis")
    print("  3. ✅ Productivity analysis")
    print("  4. ✅ Staffing shortage detection")
    print("  5. ✅ Overtime analysis")
    print("  6. ✅ Workforce anomaly detection")
    print("  7. ✅ Staffing forecasting")
    print("  8. ✅ Specific staff queries")
    print("  9. ✅ Action proposals with human approval")
    print(" 10. ✅ Unauthorized action prevention")
    print(" 11. ✅ Approval workflow")
    print("\nThe Staff Agent is working independently")
    print("and is ready for backend integration.")

def interactive_mode():
    """Run in interactive mode"""
    print_section("STAFF AGENT - INTERACTIVE MODE")
    print("Type your workforce questions. Type 'exit' to quit.")
    print("=" * 80)
    
    agent = StaffAgent(api_key=Config.GOOGLE_API_KEY if Config.USE_LLM else None)
    
    while True:
        query = input("\n📊 You: ").strip()
        if query.lower() in ['exit', 'quit', 'q']:
            break
        
        if not query:
            continue
        
        response = agent.process_query(query)
        print_response(response)
        
        # Handle pending actions
        if response.get('status') == 'PENDING_APPROVAL' and agent.pending_actions:
            print("\n📋 Pending Actions:")
            for action in agent.pending_actions:
                print(f"  {action['id']}: {action['query']}")
            
            action_input = input("\nApprove/Reject action? (a<id>/r<id>/skip): ").strip()
            if action_input.startswith('a'):
                try:
                    action_id = int(action_input[1:])
                    result = agent.approve_action(action_id)
                    print(f"✅ {result.get('message')}")
                except:
                    print("Invalid action ID")
            elif action_input.startswith('r'):
                try:
                    action_id = int(action_input[1:])
                    result = agent.reject_action(action_id)
                    print(f"❌ {result.get('message')}")
                except:
                    print("Invalid action ID")

def run_tests():
    """Run all tests"""
    print_section("RUNNING TESTS")
    print("=" * 80)
    
    agent = StaffAgent()
    passed = 0
    failed = 0
    
    # Test 1: Attendance calculation
    print("\n[TEST 1] Attendance Calculation")
    try:
        result = agent._handle_attendance_query()
        assert 'attendance_rate' in result.get('data', {})
        print("✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
        failed += 1
    
    # Test 2: Productivity calculation
    print("\n[TEST 2] Productivity Calculation")
    try:
        result = agent._handle_productivity_query()
        assert 'avg_productivity_score' in result.get('data', {})
        print("✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
        failed += 1
    
    # Test 3: Staffing shortage detection
    print("\n[TEST 3] Staffing Shortage Detection")
    try:
        result = agent._handle_shortage_query()
        assert 'shortage' in result.get('summary', '') or result.get('data')
        print("✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
        failed += 1
    
    # Test 4: Anomaly detection
    print("\n[TEST 4] Anomaly Detection")
    try:
        result = agent._handle_anomaly_query()
        assert result.get('data') is not None
        print("✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
        failed += 1
    
    # Test 5: Forecasting
    print("\n[TEST 5] Staffing Forecast")
    try:
        result = agent._handle_forecast_query()
        assert result.get('data') is not None
        print("✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
        failed += 1
    
    # Test 6: Action approval requirement
    print("\n[TEST 6] Action Approval Requirement")
    try:
        result = agent.process_query("Add new staff member")
        assert result.get('requires_approval', False) or result.get('status') == 'PENDING_APPROVAL'
        print("✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
        failed += 1
    
    # Test 7: Unauthorized action prevention
    print("\n[TEST 7] Unauthorized Action Prevention")
    try:
        result = agent.process_query("Fire employee")
        # Should either require approval or be blocked
        assert result.get('requires_approval', False) or result.get('status') == 'PENDING_APPROVAL'
        print("✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"❌ FAILED: {e}")
        failed += 1
    
    # Summary
    print(f"\n{'-' * 40}")
    print(f"TESTS PASSED: {passed}")
    print(f"TESTS FAILED: {failed}")
    print(f"TOTAL: {passed + failed}")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {failed} test(s) failed.")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" FRANCHISEOPS AI - STAFF AGENT")
    print("=" * 80)
    
    print("\nChoose mode:")
    print("  1. Full demonstration")
    print("  2. Interactive mode")
    print("  3. Run tests")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    
    if choice == "1":
        run_demonstration()
    elif choice == "2":
        interactive_mode()
    elif choice == "3":
        run_tests()
    else:
        print("Invalid choice. Running demonstration...")
        run_demonstration()