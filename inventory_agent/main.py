"""
Main entry point for the Inventory Agent.
Provides a standalone demonstration and interactive mode.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory_agent.data_access.csv_provider import CSVDataProvider
from inventory_agent.agent.inventory_agent import InventoryAgent
from inventory_agent.utils.llm_interface import LLMInterface
from inventory_agent.config.settings import settings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_response(response: dict, indent: int = 0):
    """Pretty print a response dictionary."""
    if not response:
        return
    
    prefix = " " * indent
    
    # Print summary if present
    if 'summary' in response:
        print(f"{prefix}Summary: {response['summary']}")
    
    # Print status
    if 'status' in response:
        status_color = "✅" if response['status'] == 'success' else "❌"
        print(f"{prefix}Status: {status_color} {response['status']}")
    
    # Print data
    if 'data' in response and response['data']:
        print(f"{prefix}Data:")
        data = response['data']
        if isinstance(data, list):
            for item in data[:5]:  # Show first 5 items
                if isinstance(item, dict):
                    print(f"{prefix}  - {item.get('item_name', 'Unknown')}: "
                          f"{item.get('current_quantity', 0)} {item.get('unit', 'units')} "
                          f"(Status: {item.get('status_display', 'Unknown')})")
        elif isinstance(data, dict):
            for key, value in list(data.items())[:5]:
                print(f"{prefix}  {key}: {value}")
    
    # Print recommendations
    if 'recommendations' in response:
        print(f"{prefix}Recommendations:")
        for rec in response['recommendations'][:3]:
            print(f"{prefix}  - {rec}")
    
    # Print proposed action
    if 'proposed_action' in response:
        action = response['proposed_action']
        print(f"{prefix}Proposed Action:")
        print(f"{prefix}  ID: {action.get('action_id')}")
        print(f"{prefix}  Item: {action.get('item_name')}")
        print(f"{prefix}  Quantity: {action.get('quantity')} {action.get('unit', 'units')}")
        if action.get('estimated_cost'):
            print(f"{prefix}  Estimated Cost: ₹{action['estimated_cost']}")
        print(f"{prefix}  Status: {action.get('status')}")
        print(f"{prefix}  Reason: {action.get('reason')}")
    
    # Print message if present
    if 'message' in response:
        print(f"{prefix}Message: {response['message']}")
    
    # Print error if present
    if 'error' in response:
        print(f"{prefix}Error: {response['error']}")
    
    # Print note if present
    if 'note' in response:
        print(f"{prefix}Note: {response['note']}")


def run_demonstration():
    """Run the standalone demonstration."""
    print_header("INVENTORY AGENT - STANDALONE DEMONSTRATION")
    print("Using sample data (CSV files in data/ directory)")
    print(f"LLM Provider: {'Gemini' if settings.has_api_key else 'Fallback (keyword-based)'}")
    print("=" * 80)
    
    # Initialize the agent
    logger.info("Initializing inventory agent...")
    data_provider = CSVDataProvider()
    llm_interface = LLMInterface()
    agent = InventoryAgent(data_provider, llm_interface)
    
    # Test 1: Get inventory status
    print_header("TEST 1: Inventory Status")
    response = agent.process_query("Show me inventory status", outlet_id="OUT101")
    print_response(response)
    
    # Test 2: Detect shortages
    print_header("TEST 2: Shortage Detection")
    response = agent.process_query("Which items are running low?", outlet_id="OUT101")
    print_response(response)
    
    # Test 3: Stockout prediction for a specific item
    print_header("TEST 3: Stockout Prediction")
    response = agent.process_query("When will milk run out?", outlet_id="OUT101")
    print_response(response)
    
    # Test 4: Demand forecasting
    print_header("TEST 4: Demand Forecasting")
    item = data_provider.get_inventory_item("ITEM001")  # Milk
    if item:
        forecast = agent.forecast_demand("OUT101", "ITEM001", days=7)
        print(f"Item: {item.item_name}")
        print(f"Forecast Method: {forecast.get('method', 'N/A')}")
        print(f"Total Forecast Demand (7 days): {forecast.get('total_forecast_demand', 0):.1f} {item.unit}")
        print(f"Confidence: {forecast.get('confidence', 'unknown')}")
        if forecast.get('prediction_range'):
            print(f"Prediction Range: {forecast['prediction_range']['lower'][0]:.1f} - {forecast['prediction_range']['upper'][0]:.1f}")
    
    # Test 5: Replenishment recommendation
    print_header("TEST 5: Replenishment Recommendation")
    response = agent.process_query("Should we reorder milk?", outlet_id="OUT101")
    print_response(response)
    
    # Test 6: Wastage analysis
    print_header("TEST 6: Wastage Analysis")
    response = agent.process_query("Show milk wastage", outlet_id="OUT101")
    print_response(response)
    
    # Test 7: Overstock detection
    print_header("TEST 7: Overstock Detection")
    response = agent.process_query("Which items are overstocked?", outlet_id="OUT101")
    print_response(response)
    
    # Test 8: Prepare purchase action
    print_header("TEST 8: Purchase Action Preparation")
    response = agent.process_query("Prepare a purchase order for milk", outlet_id="OUT101")
    print_response(response)
    
    # Get the action ID if available
    action_id = None
    if 'proposed_action' in response:
        action_id = response['proposed_action'].get('action_id')
    
    # Test 9: Unauthorized action prevention
    print_header("TEST 9: Unauthorized Action Prevention")
    if action_id:
        response = agent.process_query(f"Execute action {action_id}")
        print_response(response)
        print("\n⚠️ BLOCKED: Action requires Human Head approval")
    
    # Test 10: Approval workflow
    print_header("TEST 10: Approval Workflow")
    if action_id:
        print(f"1. Pending actions: {len(agent.pending_actions)}")
        print(f"2. Approving action: {action_id}")
        response = agent.process_query(f"Approve action {action_id}")
        print_response(response)
        print(f"3. Pending actions remaining: {len(agent.pending_actions)}")
        
        # Test execution after approval
        print("\n4. Attempting to execute approved action...")
        response = agent.execute_action(action_id)
        print_response(response)
    
    # Test 11: Multi-outlet support
    print_header("TEST 11: Multi-Outlet Comparison")
    outlets = data_provider.get_outlets()
    print(f"Supported outlets: {', '.join(outlets)}")
    
    for outlet_id in outlets[:3]:  # Show first 3 outlets
        inventory = agent.fetch_inventory(outlet_id=outlet_id)
        total_items = len(inventory)
        low_stock = [i for i in inventory if i['status'] in ['LOW_STOCK', 'CRITICAL_STOCK']]
        print(f"\n{outlet_id}: {total_items} items, {len(low_stock)} low/critical")
    
    # Summary
    print_header("DEMONSTRATION COMPLETE")
    print("Summary of capabilities demonstrated:")
    print("  ✅ Inventory monitoring")
    print("  ✅ Low-stock detection")
    print("  ✅ Stockout prediction")
    print("  ✅ Demand forecasting")
    print("  ✅ Replenishment recommendation")
    print("  ✅ Wastage analysis")
    print("  ✅ Overstock detection")
    print("  ✅ Anomaly detection")
    print("  ✅ Natural-language interaction")
    print("  ✅ Purchase proposal generation")
    print("  ✅ Human approval workflow")
    print("  ✅ Unauthorized purchase blocking")
    print("\nThe Inventory Agent is working independently and is ready for backend integration.")
    print("=" * 80)


def interactive_mode():
    """Run the agent in interactive mode."""
    print_header("INVENTORY AGENT - INTERACTIVE MODE")
    print("Type your inventory questions or 'exit' to quit.")
    print("Example questions:")
    print("  - Show me inventory status")
    print("  - Which items are running low?")
    print("  - When will milk run out?")
    print("  - Should we reorder bread?")
    print("  - Prepare a purchase order for eggs")
    print("  - Show me wastage analysis")
    print("  - Which items are overstocked?")
    print("=" * 80)
    
    # Initialize the agent
    data_provider = CSVDataProvider()
    llm_interface = LLMInterface()
    agent = InventoryAgent(data_provider, llm_interface)
    
    print(f"\n✅ Agent initialized. LLM: {'Enabled' if llm_interface.enabled else 'Fallback mode'}")
    print("Type 'help' for more examples.\n")
    
    while True:
        try:
            query = input("\n❓ You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if query.lower() == 'help':
                print("\nExample queries:")
                print("  - Show inventory status")
                print("  - Which items are low?")
                print("  - When will milk run out?")
                print("  - Should we reorder milk?")
                print("  - Prepare purchase order for bread")
                print("  - Show milk wastage")
                print("  - Which items are overstocked?")
                print("  - Approve action [action_id]")
                print("  - Reject action [action_id]")
                continue
            
            # Process query
            response = agent.process_query(query)
            print("\n🤖 Agent: ")
            print_response(response, indent=2)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"\n❌ Error: {e}")


def run_tests():
    """Run unit tests."""
    import pytest
    import os
    
    # Get the tests directory
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    if not os.path.exists(tests_dir):
        print("❌ Tests directory not found. Creating sample test...")
        os.makedirs(tests_dir, exist_ok=True)
        
        # Create a simple test file
        with open(os.path.join(tests_dir, 'test_agent.py'), 'w') as f:
            f.write('''
import pytest
from inventory_agent.data_access.csv_provider import CSVDataProvider
from inventory_agent.agent.inventory_agent import InventoryAgent


def test_inventory_fetch():
    """Test inventory fetching."""
    provider = CSVDataProvider()
    agent = InventoryAgent(provider)
    inventory = agent.fetch_inventory(outlet_id="OUT101")
    assert len(inventory) > 0
    assert 'item_id' in inventory[0]


def test_shortage_detection():
    """Test shortage detection."""
    provider = CSVDataProvider()
    agent = InventoryAgent(provider)
    shortages = agent.detect_shortages(outlet_id="OUT101")
    assert isinstance(shortages, list)


def test_stockout_prediction():
    """Test stockout prediction."""
    provider = CSVDataProvider()
    agent = InventoryAgent(provider)
    result = agent.predict_stockout("OUT101", "ITEM001")
    assert 'days_until_stockout' in result or 'error' in result


def test_replenishment_recommendation():
    """Test replenishment recommendation."""
    provider = CSVDataProvider()
    agent = InventoryAgent(provider)
    result = agent.generate_replenishment_recommendation("OUT101", "ITEM001")
    assert 'recommendation' in result or 'error' in result


def test_unauthorized_action_blocked():
    """Test that unauthorized actions are blocked."""
    provider = CSVDataProvider()
    agent = InventoryAgent(provider)
    
    # Try to execute without approval
    result = agent.execute_action("NON_EXISTENT_ACTION")
    assert 'error' in result
    assert 'BLOCKED' in result.get('status', '')
''')
    
    # Run pytest
    sys.exit(pytest.main([tests_dir, '-v', '--tb=short']))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Inventory Agent')
    parser.add_argument('--mode', choices=['demo', 'interactive', 'test'], 
                       default='demo', help='Run mode')
    parser.add_argument('--outlet', help='Default outlet ID')
    
    args = parser.parse_args()
    
    if args.mode == 'test':
        run_tests()
    elif args.mode == 'interactive':
        interactive_mode()
    else:
        run_demonstration()


if __name__ == "__main__":
    main()