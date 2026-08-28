"""
Main Inventory Agent implementation.
Orchestrates analysis, forecasting, and recommendations.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from decimal import Decimal
import uuid
import logging
from enum import Enum

from ..data_access.interfaces import (
    DataAccessInterface, InventoryItem, StockLevel, DemandHistory,
    StockMovement, SupplierInfo
)
from ..analytics.stock_analyzer import StockAnalyzer, StockStatus
from ..forecasting.demand_forecaster import DemandForecaster
from ..utils.llm_interface import LLMInterface
from ..config.settings import settings


logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Approval status for proposed actions."""
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class InventoryAgent:
    """
    Main Inventory Agent responsible for inventory intelligence.
    """
    
    def __init__(self, data_provider: DataAccessInterface,
                 llm_interface: Optional[LLMInterface] = None):
        """
        Initialize the Inventory Agent.
        
        Args:
            data_provider: Data access implementation
            llm_interface: LLM interface for natural language processing
        """
        self.data_provider = data_provider
        self.llm_interface = llm_interface or LLMInterface()
        self.stock_analyzer = StockAnalyzer()
        self.demand_forecaster = DemandForecaster()
        self.pending_actions: List[Dict] = []
        self.approved_actions: List[Dict] = []
        
        logger.info("InventoryAgent initialized")
    
    def fetch_inventory(self, outlet_id: Optional[str] = None,
                       item_id: Optional[str] = None) -> List[Dict]:
        """
        Fetch current inventory levels.
        """
        stock_levels = self.data_provider.get_stock_levels(
            outlet_id=outlet_id, item_id=item_id
        )
        
        results = []
        for stock in stock_levels:
            item = self.data_provider.get_inventory_item(stock.item_id)
            demand_history = self.data_provider.get_demand_history(
                outlet_id=stock.outlet_id,
                item_id=stock.item_id
            )
            
            avg_demand = self.stock_analyzer.calculate_average_daily_demand(
                demand_history, days=30
            )
            
            coverage = self.stock_analyzer.calculate_stock_coverage(
                stock.current_quantity, avg_demand
            )
            
            status = self.stock_analyzer.get_stock_status(
                stock.current_quantity, avg_demand, coverage
            )
            
            results.append({
                'outlet_id': stock.outlet_id,
                'item_id': stock.item_id,
                'item_name': item.item_name if item else 'Unknown',
                'current_quantity': stock.current_quantity,
                'unit': item.unit if item else 'units',
                'average_daily_demand': avg_demand,
                'coverage_days': coverage,
                'status': status.value,
                'status_display': status.name.replace('_', ' ').title()
            })
        
        return results
    
    def forecast_demand(self, outlet_id: str, item_id: str,
                       days: int = 7) -> Dict:
        """
        Forecast demand for a specific item at a specific outlet.
        """
        demand_history = self.data_provider.get_demand_history(
            outlet_id=outlet_id,
            item_id=item_id
        )
        
        if not demand_history:
            return {
                'outlet_id': outlet_id,
                'item_id': item_id,
                'forecast_days': days,
                'forecast': [],
                'error': 'No historical demand data available',
                'confidence': 'unknown'
            }
        
        forecast_result = self.demand_forecaster.forecast(
            demand_history, forecast_days=days
        )
        
        item = self.data_provider.get_inventory_item(item_id)
        
        return {
            'outlet_id': outlet_id,
            'item_id': item_id,
            'item_name': item.item_name if item else 'Unknown',
            'forecast_days': days,
            'forecast': forecast_result['forecast'],
            'total_forecast_demand': forecast_result['total_forecast_demand'],
            'method': forecast_result['method'],
            'confidence': forecast_result['confidence'],
            'prediction_range': forecast_result.get('prediction_range'),
            'mean_demand': forecast_result.get('mean_demand', 0),
            'unit': item.unit if item else 'units'
        }
    
    def predict_stockout(self, outlet_id: str, item_id: str) -> Dict:
        """
        Predict when stockout might occur.
        """
        stock_levels = self.data_provider.get_stock_levels(
            outlet_id=outlet_id, item_id=item_id
        )
        
        if not stock_levels:
            return {
                'outlet_id': outlet_id,
                'item_id': item_id,
                'error': 'No stock data available'
            }
        
        stock = stock_levels[0]
        demand_history = self.data_provider.get_demand_history(
            outlet_id=outlet_id, item_id=item_id
        )
        
        avg_demand = self.stock_analyzer.calculate_average_daily_demand(
            demand_history, days=30
        )
        
        if avg_demand <= 0:
            return {
                'outlet_id': outlet_id,
                'item_id': item_id,
                'current_stock': stock.current_quantity,
                'average_daily_demand': 0,
                'days_until_stockout': None,
                'error': 'Cannot predict stockout: no demand data'
            }
        
        days_until_stockout = stock.current_quantity / avg_demand
        
        # Get forecast for more accurate prediction
        forecast_result = self.forecast_demand(outlet_id, item_id, days=14)
        
        return {
            'outlet_id': outlet_id,
            'item_id': item_id,
            'current_stock': stock.current_quantity,
            'average_daily_demand': avg_demand,
            'days_until_stockout': days_until_stockout,
            'forecast_demand_7days': forecast_result.get('total_forecast_demand', 0),
            'confidence': 'medium' if len(demand_history) >= 30 else 'low',
            'stockout_risk': 'HIGH' if days_until_stockout <= 3 else 'MEDIUM' if days_until_stockout <= 7 else 'LOW'
        }
    
    def detect_shortages(self, outlet_id: Optional[str] = None) -> List[Dict]:
        """
        Detect current and impending shortages.
        """
        shortages = []
        inventory = self.fetch_inventory(outlet_id=outlet_id)
        
        for item in inventory:
            if item['status'] in ['LOW_STOCK', 'CRITICAL_STOCK', 'STOCKOUT']:
                # Check supplier info
                item_obj = self.data_provider.get_inventory_item(item['item_id'])
                suppliers = self.data_provider.get_supplier_info(
                    supplier_id=item_obj.supplier_id if item_obj else None
                )
                
                lead_time = suppliers[0].lead_time_days if suppliers else None
                
                shortages.append({
                    **item,
                    'status': item['status'],
                    'severity': 'HIGH' if item['status'] == 'STOCKOUT' 
                               else 'MEDIUM' if item['status'] == 'CRITICAL_STOCK'
                               else 'LOW',
                    'lead_time_days': lead_time,
                    'recommendation': self._get_shortage_recommendation(item, lead_time)
                })
        
        return shortages
    
    def _get_shortage_recommendation(self, item: Dict, lead_time: Optional[int]) -> str:
        """Generate recommendation for shortage."""
        if item['status'] == 'STOCKOUT':
            return 'Immediate replenishment required'
        elif item['status'] == 'CRITICAL_STOCK':
            if lead_time and item['coverage_days'] and item['coverage_days'] < lead_time:
                return 'Replenish urgently - coverage less than lead time'
            return 'Replenish as soon as possible'
        elif item['status'] == 'LOW_STOCK':
            if lead_time and item['coverage_days'] and item['coverage_days'] < lead_time:
                return 'Replenish soon - may stockout before delivery'
            return 'Monitor and plan replenishment'
        return ''
    
    def generate_replenishment_recommendation(self, outlet_id: str, item_id: str) -> Dict:
        """
        Generate a replenishment recommendation for a specific item.
        """
        # Get current stock
        stock_levels = self.data_provider.get_stock_levels(
            outlet_id=outlet_id, item_id=item_id
        )
        
        if not stock_levels:
            return {
                'error': f'No stock data found for item {item_id} at outlet {outlet_id}'
            }
        
        stock = stock_levels[0]
        item = self.data_provider.get_inventory_item(item_id)
        suppliers = self.data_provider.get_supplier_info(
            supplier_id=item.supplier_id if item else None
        )
        supplier = suppliers[0] if suppliers else None
        
        # Get demand forecast
        forecast = self.forecast_demand(outlet_id, item_id, days=7)
        
        # Get historical demand for variability calculation
        demand_history = self.data_provider.get_demand_history(
            outlet_id=outlet_id, item_id=item_id
        )
        avg_demand = self.stock_analyzer.calculate_average_daily_demand(
            demand_history, days=30
        )
        
        # Calculate safety stock
        safety_stock = supplier.safety_stock if supplier else 0
        lead_time_days = supplier.lead_time_days if supplier else 3  # Default if not available
        
        # Calculate reorder point
        reorder_point = avg_demand * lead_time_days + safety_stock
        
        # Determine if reorder is needed
        current_stock = stock.current_quantity
        recommended_quantity = 0
        recommendation = 'NO_REORDER_REQUIRED'
        reason = ''
        stock_cover_days = self.stock_analyzer.calculate_stock_coverage(
            current_stock, avg_demand
        )
        
        if current_stock <= reorder_point:
            recommended_quantity = (forecast.get('total_forecast_demand', 0) + 
                                   safety_stock - current_stock)
            if supplier and supplier.minimum_order_quantity:
                recommended_quantity = max(recommended_quantity, 
                                          supplier.minimum_order_quantity)
            recommendation = 'REORDER_NOW'
            reason = f'Current stock ({current_stock:.1f}) is below reorder point ({reorder_point:.1f})'
        elif current_stock <= reorder_point * 1.2:
            recommendation = 'REORDER_SOON'
            reason = f'Current stock ({current_stock:.1f}) is approaching reorder point ({reorder_point:.1f})'
        elif current_stock > avg_demand * 14:
            recommendation = 'REDUCE_ORDERING'
            reason = f'Current stock ({current_stock:.1f}) exceeds 14 days of demand'
        else:
            recommendation = 'MONITOR'
            reason = f'Current stock ({current_stock:.1f}) is adequate for {stock_cover_days:.1f} days'
        
        # Calculate estimated cost
        estimated_cost = None
        if item and item.unit_cost and recommended_quantity > 0:
            estimated_cost = item.unit_cost * Decimal(str(recommended_quantity))
        
        return {
            'outlet_id': outlet_id,
            'item_id': item_id,
            'item_name': item.item_name if item else 'Unknown',
            'current_stock': current_stock,
            'average_daily_demand': avg_demand,
            'stock_coverage_days': stock_cover_days,
            'reorder_point': reorder_point,
            'safety_stock': safety_stock,
            'lead_time_days': lead_time_days,
            'recommendation': recommendation,
            'recommendation_display': recommendation.replace('_', ' ').title(),
            'recommended_quantity': max(0, recommended_quantity),
            'estimated_cost': estimated_cost,
            'reason': reason,
            'unit': item.unit if item else 'units'
        }
    
    def prepare_purchase_action(self, outlet_id: str, item_id: str,
                               quantity: Optional[float] = None) -> Dict:
        """
        Prepare a proposed purchase action for Human Head approval.
        """
        # Get recommendation
        recommendation = self.generate_replenishment_recommendation(
            outlet_id, item_id
        )
        
        if 'error' in recommendation:
            return recommendation
        
        # Use recommended quantity if not specified
        if quantity is None:
            quantity = recommendation.get('recommended_quantity', 0)
        
        if quantity <= 0:
            return {
                'error': 'No purchase required at this time',
                'recommendation': recommendation
            }
        
        item = self.data_provider.get_inventory_item(item_id)
        estimated_cost = None
        if item and item.unit_cost:
            estimated_cost = item.unit_cost * Decimal(str(quantity))
        
        # Create proposed action
        action_id = f"ACT_{uuid.uuid4().hex[:8].upper()}"
        
        proposed_action = {
            'action_id': action_id,
            'action_type': 'INVENTORY_REPLENISHMENT',
            'outlet_id': outlet_id,
            'item_id': item_id,
            'item_name': item.item_name if item else 'Unknown',
            'quantity': quantity,
            'unit': item.unit if item else 'units',
            'estimated_cost': estimated_cost,
            'reason': recommendation.get('reason', 'Replenishment recommended'),
            'risk_level': recommendation.get('recommendation', 'MONITOR'),
            'status': ApprovalStatus.PENDING_APPROVAL.value,
            'requires_human_approval': True,
            'created_at': datetime.now().isoformat(),
            'recommendation_details': recommendation
        }
        
        # Store pending action
        self.pending_actions.append(proposed_action)
        
        return proposed_action
    
    def approve_action(self, action_id: str) -> Dict:
        """
        Approve a pending action.
        """
        # Find the action
        action = None
        for idx, pending in enumerate(self.pending_actions):
            if pending.get('action_id') == action_id:
                action = pending
                break
        
        if not action:
            return {
                'error': f'Action {action_id} not found or already processed'
            }
        
        # Update status
        action['status'] = ApprovalStatus.APPROVED.value
        action['approved_at'] = datetime.now().isoformat()
        
        # Move to approved list
        self.pending_actions = [
            a for a in self.pending_actions 
            if a.get('action_id') != action_id
        ]
        self.approved_actions.append(action)
        
        return {
            'message': f'Action {action_id} approved successfully',
            'action': action,
            'note': 'No purchase was executed because no procurement execution system is connected.'
        }
    
    def reject_action(self, action_id: str, reason: Optional[str] = None) -> Dict:
        """
        Reject a pending action.
        """
        action = None
        for idx, pending in enumerate(self.pending_actions):
            if pending.get('action_id') == action_id:
                action = pending
                break
        
        if not action:
            return {
                'error': f'Action {action_id} not found'
            }
        
        action['status'] = ApprovalStatus.REJECTED.value
        action['rejected_at'] = datetime.now().isoformat()
        action['rejection_reason'] = reason or 'No reason provided'
        
        self.pending_actions = [
            a for a in self.pending_actions 
            if a.get('action_id') != action_id
        ]
        
        return {
            'message': f'Action {action_id} rejected',
            'action': action
        }
    
    def execute_action(self, action_id: str) -> Dict:
        """
        Execute an approved action.
        This is BLOCKED without explicit Human Head approval.
        """
        # Check if action is approved
        action = None
        for approved in self.approved_actions:
            if approved.get('action_id') == action_id:
                action = approved
                break
        
        if not action:
            # Check if it's pending
            for pending in self.pending_actions:
                if pending.get('action_id') == action_id:
                    return {
                        'error': 'Action is pending approval. Human Head approval required.',
                        'status': 'BLOCKED',
                        'action': pending
                    }
            
            return {
                'error': f'Action {action_id} not found',
                'status': 'BLOCKED'
            }
        
        if action.get('status') != ApprovalStatus.APPROVED.value:
            return {
                'error': f'Action {action_id} is not approved (status: {action.get("status")})',
                'status': 'BLOCKED'
            }
        
        # Execute the action (simulated)
        return {
            'message': f'Action {action_id} executed successfully (simulated)',
            'action': action,
            'note': 'This is a simulation. No actual purchase was made.'
        }
    
    def process_query(self, query: str, outlet_id: Optional[str] = None) -> Dict:
        """
        Process a natural language query.
        """
        # Try to understand intent with LLM
        intent_result = self._detect_intent(query)
        
        # Extract entities
        entities = intent_result.get('entities', {})
        item_name = entities.get('item_name')
        item_id = entities.get('item_id')
        
        # If item name provided but not ID, find it
        if item_name and not item_id:
            items = self.data_provider.get_inventory_items()
            for item in items:
                if item_name.lower() in item.item_name.lower():
                    item_id = item.item_id
                    break
        
        # Handle different intents
        intent = intent_result.get('intent', 'unknown')
        
        if intent == 'inventory_status':
            return self._handle_inventory_query(entity_id=item_id, outlet_id=outlet_id)
        elif intent == 'shortage_detection':
            return self._handle_shortage_query(outlet_id=outlet_id)
        elif intent == 'stockout_prediction':
            return self._handle_stockout_query(entity_id=item_id, outlet_id=outlet_id)
        elif intent == 'replenishment':
            return self._handle_replenishment_query(entity_id=item_id, outlet_id=outlet_id)
        elif intent == 'wastage_analysis':
            return self._handle_wastage_query(entity_id=item_id, outlet_id=outlet_id)
        elif intent == 'overstock_detection':
            return self._handle_overstock_query(outlet_id=outlet_id)
        elif intent == 'purchase_action':
            return self._handle_purchase_action_query(entity_id=item_id, outlet_id=outlet_id)
        elif intent == 'approval':
            return self._handle_approval_query(query)
        elif intent == 'unauthorized_action':
            return self._handle_unauthorized_action()
        else:
            return {
                'intent': 'unknown',
                'status': 'error',
                'summary': f"I couldn't understand your query: '{query}'",
                'query': query
            }
    
    def _detect_intent(self, query: str) -> Dict:
        """Detect intent using LLM or fallback."""
        if self.llm_interface and self.llm_interface.enabled:
            try:
                return self.llm_interface.detect_intent(query)
            except Exception as e:
                logger.warning(f"LLM intent detection failed: {e}")
        
        # Fallback: keyword-based detection
        return self._fallback_intent_detection(query)
    
    def _fallback_intent_detection(self, query: str) -> Dict:
        """Fallback intent detection using keywords."""
        query_lower = query.lower()
        intent = 'unknown'
        entities = {}
        
        # Check for item names
        items = self.data_provider.get_inventory_items()
        for item in items:
            if item.item_name.lower() in query_lower:
                entities['item_name'] = item.item_name
                entities['item_id'] = item.item_id
                break
        
        # Detect intent
        if any(word in query_lower for word in ['shortage', 'low', 'running low', 'critical']):
            intent = 'shortage_detection'
        elif any(word in query_lower for word in ['stockout', 'out of stock', 'run out']):
            intent = 'stockout_prediction'
        elif any(word in query_lower for word in ['reorder', 'order', 'replenish', 'buy']):
            if any(word in query_lower for word in ['prepare', 'propose']):
                intent = 'purchase_action'
            elif any(word in query_lower for word in ['approve']):
                intent = 'approval'
            else:
                intent = 'replenishment'
        elif any(word in query_lower for word in ['waste', 'wastage']):
            intent = 'wastage_analysis'
        elif any(word in query_lower for word in ['overstock', 'excess', 'too much']):
            intent = 'overstock_detection'
        elif any(word in query_lower for word in ['inventory', 'stock', 'quantity', 'how much']):
            intent = 'inventory_status'
        elif any(word in query_lower for word in ['place', 'execute', 'action']):
            if any(word in query_lower for word in ['without', 'no', 'not']):
                intent = 'unauthorized_action'
            else:
                intent = 'purchase_action'
        else:
            intent = 'inventory_status'  # Default to inventory status
        
        return {'intent': intent, 'entities': entities}
    
    def _handle_inventory_query(self, entity_id: Optional[str] = None,
                                outlet_id: Optional[str] = None) -> Dict:
        """Handle inventory status query."""
        inventory = self.fetch_inventory(outlet_id=outlet_id, item_id=entity_id)
        
        if not inventory:
            return {
                'intent': 'inventory_status',
                'status': 'error',
                'summary': 'No inventory data found',
                'data': []
            }
        
        # Calculate summary statistics
        total_items = len(inventory)
        low_stock_items = [i for i in inventory if i['status'] in ['LOW_STOCK', 'CRITICAL_STOCK']]
        
        summary = f"Found {total_items} inventory items. "
        if low_stock_items:
            summary += f"{len(low_stock_items)} items are low or critical."
        
        return {
            'intent': 'inventory_status',
            'status': 'success',
            'summary': summary,
            'data': inventory,
            'low_stock_items': low_stock_items
        }
    
    def _handle_shortage_query(self, outlet_id: Optional[str] = None) -> Dict:
        """Handle shortage detection query."""
        shortages = self.detect_shortages(outlet_id=outlet_id)
        
        if not shortages:
            return {
                'intent': 'shortage_detection',
                'status': 'success',
                'summary': 'No shortages detected',
                'data': []
            }
        
        summary = f"Found {len(shortages)} items with shortages or low stock."
        urgent = [s for s in shortages if s.get('severity') == 'HIGH']
        if urgent:
            summary += f" {len(urgent)} items require immediate attention."
        
        return {
            'intent': 'shortage_detection',
            'status': 'success',
            'summary': summary,
            'data': shortages,
            'urgent_items': urgent
        }
    
    def _handle_stockout_query(self, entity_id: Optional[str] = None,
                               outlet_id: Optional[str] = None) -> Dict:
        """Handle stockout prediction query."""
        if entity_id:
            # Single item prediction
            result = self.predict_stockout(outlet_id=outlet_id or 'OUT101', 
                                          item_id=entity_id)
            return {
                'intent': 'stockout_prediction',
                'status': 'success' if 'error' not in result else 'partial',
                'data': result,
                'summary': self._format_stockout_summary(result)
            }
        else:
            # Check all items
            items = self.data_provider.get_inventory_items()
            results = []
            for item in items:
                result = self.predict_stockout(
                    outlet_id=outlet_id or 'OUT101', 
                    item_id=item.item_id
                )
                if 'error' not in result:
                    results.append(result)
            
            high_risk = [r for r in results if r.get('stockout_risk') == 'HIGH']
            summary = f"Checked {len(results)} items. {len(high_risk)} items have high stockout risk."
            
            return {
                'intent': 'stockout_prediction',
                'status': 'success',
                'data': results,
                'high_risk_items': high_risk,
                'summary': summary
            }
    
    def _format_stockout_summary(self, result: Dict) -> str:
        """Format stockout prediction summary."""
        if 'error' in result:
            return result['error']
        
        days = result.get('days_until_stockout')
        if days is None:
            return "Cannot predict stockout due to insufficient data"
        
        return f"Stockout predicted in approximately {days:.1f} days. Risk: {result.get('stockout_risk', 'UNKNOWN')}"
    
    def _handle_replenishment_query(self, entity_id: Optional[str] = None,
                                    outlet_id: Optional[str] = None) -> Dict:
        """Handle replenishment recommendation query."""
        if not entity_id:
            return {
                'intent': 'replenishment',
                'status': 'error',
                'summary': 'Please specify which item needs replenishment.'
            }
        
        recommendation = self.generate_replenishment_recommendation(
            outlet_id=outlet_id or 'OUT101',
            item_id=entity_id
        )
        
        if 'error' in recommendation:
            return {
                'intent': 'replenishment',
                'status': 'error',
                'summary': recommendation['error']
            }
        
        return {
            'intent': 'replenishment',
            'status': 'success',
            'data': recommendation,
            'summary': f"{recommendation.get('recommendation_display')}: {recommendation.get('reason')}"
        }
    
    def _handle_wastage_query(self, entity_id: Optional[str] = None,
                              outlet_id: Optional[str] = None) -> Dict:
        """Handle wastage analysis query."""
        # Get movements
        movements = self.data_provider.get_stock_movements(
            outlet_id=outlet_id,
            item_id=entity_id
        )
        
        if not movements:
            return {
                'intent': 'wastage_analysis',
                'status': 'error',
                'summary': 'No movement data available for wastage analysis'
            }
        
        wastage_rate = self.stock_analyzer.calculate_wastage_rate(movements)
        
        # Get wasted quantities
        total_waste = sum(m.quantity_wasted for m in movements)
        total_used = sum(m.quantity_used for m in movements)
        
        summary = f"Wastage rate: {wastage_rate:.1f}% "
        if wastage_rate > settings.WASTAGE_THRESHOLD_PERCENT:
            summary += "(Above threshold)"
        
        return {
            'intent': 'wastage_analysis',
            'status': 'success',
            'data': {
                'total_waste': total_waste,
                'total_used': total_used,
                'wastage_rate': wastage_rate,
                'above_threshold': wastage_rate > settings.WASTAGE_THRESHOLD_PERCENT,
                'threshold': settings.WASTAGE_THRESHOLD_PERCENT
            },
            'summary': summary
        }
    
    def _handle_overstock_query(self, outlet_id: Optional[str] = None) -> Dict:
        """Handle overstock detection query."""
        inventory = self.fetch_inventory(outlet_id=outlet_id)
        
        overstocked = [i for i in inventory if i['status'] == 'OVERSTOCKED']
        
        if not overstocked:
            return {
                'intent': 'overstock_detection',
                'status': 'success',
                'summary': 'No overstocked items detected',
                'data': []
            }
        
        summary = f"Found {len(overstocked)} overstocked items."
        return {
            'intent': 'overstock_detection',
            'status': 'success',
            'data': overstocked,
            'summary': summary
        }
    
    def _handle_purchase_action_query(self, entity_id: Optional[str] = None,
                                     outlet_id: Optional[str] = None) -> Dict:
        """Handle purchase action preparation."""
        if not entity_id:
            return {
                'intent': 'purchase_action',
                'status': 'error',
                'summary': 'Please specify which item to purchase.'
            }
        
        action = self.prepare_purchase_action(
            outlet_id=outlet_id or 'OUT101',
            item_id=entity_id
        )
        
        if 'error' in action:
            return {
                'intent': 'purchase_action',
                'status': 'error',
                'summary': action['error']
            }
        
        return {
            'intent': 'purchase_action',
            'status': 'success',
            'requires_human_approval': True,
            'proposed_action': action,
            'summary': f"Purchase proposal prepared for {action.get('quantity')} {action.get('unit')} of {action.get('item_name')}. PENDING_APPROVAL."
        }
    
    def _handle_approval_query(self, query: str) -> Dict:
        """Handle approval query."""
        # Try to extract action ID from query
        import re
        action_id_match = re.search(r'ACT_[A-Z0-9]{8}', query)
        
        if not action_id_match:
            # List pending actions
            if not self.pending_actions:
                return {
                    'intent': 'approval',
                    'status': 'success',
                    'summary': 'No pending actions to approve',
                    'pending_actions': []
                }
            
            return {
                'intent': 'approval',
                'status': 'success',
                'summary': f"Found {len(self.pending_actions)} pending actions. Please specify which action to approve by ID.",
                'pending_actions': self.pending_actions
            }
        
        action_id = action_id_match.group(0)
        
        # Check if action is pending
        pending = None
        for action in self.pending_actions:
            if action.get('action_id') == action_id:
                pending = action
                break
        
        if not pending:
            return {
                'intent': 'approval',
                'status': 'error',
                'summary': f'Action {action_id} not found or already processed'
            }
        
        # Get approval intent
        if 'reject' in query.lower():
            result = self.reject_action(action_id)
            return {
                'intent': 'approval',
                'status': 'success',
                'summary': result['message'],
                'action': result['action']
            }
        else:
            # Default to approve
            result = self.approve_action(action_id)
            return {
                'intent': 'approval',
                'status': 'success',
                'summary': result['message'],
                'action': result['action']
            }
    
    def _handle_unauthorized_action(self) -> Dict:
        """Handle unauthorized action attempt."""
        return {
            'intent': 'unauthorized_action',
            'status': 'BLOCKED',
            'summary': 'Action blocked. Human Head approval is required before executing a financially consequential purchase.',
            'requires_human_approval': True,
            'message': 'BLOCKED'
        }