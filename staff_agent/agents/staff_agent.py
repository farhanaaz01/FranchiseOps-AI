import logging
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime

from staff_agent.utils.analytics import WorkforceAnalytics
from staff_agent.utils.llm_interface import LLMInterface
from staff_agent.data_access.data_provider import DataProvider

logger = logging.getLogger(__name__)

class StaffAgent:
    """Staff/Workforce Intelligence Agent"""
    
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        self.data_provider = DataProvider()
        self.analytics = WorkforceAnalytics(self.data_provider)
        self.llm = LLMInterface(api_key, model) if api_key else None
        
        self.pending_actions = []
        self.approved_actions = []
        self.rejected_actions = []
        
        logger.info("StaffAgent initialized")
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a natural language query"""
        try:
            # 1. Detect intent
            intent_data = self._detect_intent(query)
            
            # 2. Execute based on intent
            response = self._execute_intent(intent_data, query)
            
            # 3. Check if action requires approval
            if response.get('requires_approval', False):
                response['status'] = 'PENDING_APPROVAL'
                response['message'] = 'This action requires Human Head approval.'
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "status": "error",
                "error": str(e),
                "requires_approval": False
            }
    
    def _detect_intent(self, query: str) -> Dict[str, Any]:
        """Detect intent using LLM or fallback"""
        if self.llm and self.llm.available:
            return self.llm.detect_intent(query)
        
        # Fallback
        return self._fallback_intent(query)
    
    def _fallback_intent(self, query: str) -> Dict[str, Any]:
        """Fallback intent detection"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['hire', 'fire', 'suspend', 'salary', 'bonus', 'overtime']):
            return {"intent": "action_proposal", "requires_approval": True}
        elif any(word in query_lower for word in ['attendance', 'absent', 'late']):
            return {"intent": "attendance_analysis"}
        elif any(word in query_lower for word in ['productivity', 'performance', 'tasks']):
            return {"intent": "productivity_analysis"}
        elif any(word in query_lower for word in ['understaff', 'shortage', 'need more']):
            return {"intent": "shortage_detection"}
        elif any(word in query_lower for word in ['compare', 'vs', 'versus']):
            return {"intent": "performance_comparison"}
        elif any(word in query_lower for word in ['forecast', 'predict', 'future']):
            return {"intent": "forecasting"}
        else:
            return {"intent": "general_inquiry"}
    
    def _execute_intent(self, intent_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Execute the detected intent"""
        intent = intent_data.get('intent', 'general_inquiry')
        
        if intent == 'attendance_analysis':
            return self._handle_attendance_query(query)
        elif intent == 'productivity_analysis':
            return self._handle_productivity_query(query)
        elif intent == 'staffing_levels':
            return self._handle_staffing_query()
        elif intent == 'shortage_detection':
            return self._handle_shortage_query()
        elif intent == 'performance_comparison':
            return self._handle_comparison_query()
        elif intent == 'anomaly_detection':
            return self._handle_anomaly_query()
        elif intent == 'overtime_analysis':
            return self._handle_overtime_query()
        elif intent == 'forecasting':
            return self._handle_forecast_query()
        elif intent == 'specific_staff':
            return self._handle_staff_specific(query)
        elif intent == 'action_proposal':
            return self._handle_action_proposal(query)
        else:
            return self._handle_general_query()
    
    def _handle_attendance_query(self, query: str = None) -> Dict[str, Any]:
        """Handle attendance-related queries"""
        metrics = self.analytics.calculate_attendance_metrics()
        
        response = {
            "intent": "attendance_analysis",
            "status": "success",
            "summary": f"Overall attendance rate is {metrics.get('attendance_rate', 0)}%",
            "data": metrics,
            "insights": [],
            "recommendations": [],
            "requires_approval": False
        }
        
        # Add insights
        if metrics.get('attendance_rate', 100) < 85:
            response['insights'].append("Attendance rate is below target.")
            response['recommendations'].append({
                "finding": "Low attendance rate",
                "recommendation": "Review attendance policies and individual cases",
                "requires_approval": False
            })
        
        if metrics.get('late_days', 0) > 5:
            response['insights'].append(f"{metrics['late_days']} late arrivals detected.")
        
        return response
    
    def _handle_productivity_query(self, query: str = None) -> Dict[str, Any]:
        """Handle productivity-related queries"""
        metrics = self.analytics.calculate_productivity()
        
        response = {
            "intent": "productivity_analysis",
            "status": "success",
            "summary": f"Average productivity score: {metrics.get('avg_productivity_score', 0)}",
            "data": metrics,
            "insights": [],
            "recommendations": [],
            "requires_approval": False
        }
        
        if metrics.get('avg_productivity_score', 1) < 0.6:
            response['insights'].append("Productivity is below target.")
            response['recommendations'].append({
                "finding": "Low productivity",
                "recommendation": "Review workload and consider training",
                "requires_approval": False
            })
        
        if metrics.get('trend') == 'decreasing':
            response['insights'].append(f"Productivity is decreasing ({metrics.get('trend_percentage', 0)}%)")
        
        return response
    
    def _handle_staffing_query(self) -> Dict[str, Any]:
        """Handle staffing level queries"""
        levels = self.analytics.analyze_staffing_levels()
        
        response = {
            "intent": "staffing_levels",
            "status": "success",
            "summary": f"Analyzed {len(levels)} outlets",
            "data": levels,
            "insights": [],
            "recommendations": [],
            "requires_approval": False
        }
        
        for outlet, data in levels.items():
            if data['shortage'] > 0:
                response['insights'].append(f"Outlet {outlet} needs {data['shortage']} more staff")
        
        return response
    
    def _handle_shortage_query(self) -> Dict[str, Any]:
        """Handle staffing shortage detection"""
        levels = self.analytics.analyze_staffing_levels()
        
        shortages = []
        for outlet, data in levels.items():
            if data['shortage'] > 0:
                shortages.append({
                    "outlet": outlet,
                    "shortage": data['shortage'],
                    "details": data
                })
        
        response = {
            "intent": "shortage_detection",
            "status": "success",
            "summary": f"Found {len(shortages)} outlets with staffing shortages",
            "data": shortages,
            "insights": [],
            "recommendations": [],
            "requires_approval": False
        }
        
        for shortage in shortages:
            response['recommendations'].append({
                "finding": f"Staff shortage at {shortage['outlet']}",
                "recommendation": f"Add {shortage['shortage']} staff members",
                "requires_approval": True,
                "proposed_action": f"Add {shortage['shortage']} staff to {shortage['outlet']}"
            })
        
        return response
    
    def _handle_comparison_query(self) -> Dict[str, Any]:
        """Handle performance comparison"""
        staff_df = self.data_provider.get_staff()
        perf_df = self.data_provider.get_performance()
        
        # Simple comparison by outlet
        outlet_perf = perf_df.groupby('outlet_id')['productivity_score'].mean().reset_index()
        
        response = {
            "intent": "performance_comparison",
            "status": "success",
            "summary": "Performance comparison by outlet",
            "data": outlet_perf.to_dict('records'),
            "insights": [],
            "recommendations": [],
            "requires_approval": False
        }
        
        return response
    
    def _handle_anomaly_query(self) -> Dict[str, Any]:
        """Handle anomaly detection"""
        anomalies = self.analytics.detect_anomalies()
        
        response = {
            "intent": "anomaly_detection",
            "status": "success",
            "summary": f"Found {len(anomalies)} anomalies",
            "data": anomalies,
            "insights": [],
            "recommendations": [],
            "requires_approval": False
        }
        
        for anomaly in anomalies:
            if anomaly['severity'] == 'High':
                response['recommendations'].append({
                    "finding": f"{anomaly['type']} for {anomaly['staff_id']}",
                    "recommendation": "Immediate review required",
                    "requires_approval": True,
                    "proposed_action": f"Review {anomaly['staff_id']}"
                })
        
        return response
    
    def _handle_overtime_query(self) -> Dict[str, Any]:
        """Handle overtime analysis"""
        attendance_df = self.data_provider.get_attendance()
        
        if 'overtime_hours' not in attendance_df.columns:
            return {
                "intent": "overtime_analysis",
                "status": "error",
                "error": "Overtime data not available"
            }
        
        overtime_by_staff = attendance_df.groupby('staff_id')['overtime_hours'].sum().reset_index()
        
        response = {
            "intent": "overtime_analysis",
            "status": "success",
            "summary": f"Total overtime: {overtime_by_staff['overtime_hours'].sum():.1f} hours",
            "data": overtime_by_staff.to_dict('records'),
            "insights": [],
            "recommendations": [],
            "requires_approval": False
        }
        
        high_overtime = overtime_by_staff[overtime_by_staff['overtime_hours'] > 20]
        for _, row in high_overtime.iterrows():
            response['insights'].append(f"{row['staff_id']}: {row['overtime_hours']:.1f} hours overtime")
            response['recommendations'].append({
                "finding": f"High overtime for {row['staff_id']}",
                "recommendation": "Review workload distribution",
                "requires_approval": False
            })
        
        return response
    
    def _handle_forecast_query(self) -> Dict[str, Any]:
        """Handle staffing forecast"""
        forecast = self.analytics.forecast_staffing()
        
        response = {
            "intent": "forecasting",
            "status": "success",
            "summary": f"Generated forecast for {len(forecast)} days",
            "data": forecast,
            "insights": [],
            "recommendations": [],
            "requires_approval": False
        }
        
        return response
    
    def _handle_staff_specific(self, query: str) -> Dict[str, Any]:
        """Handle staff-specific queries"""
        # Extract staff ID from query
        import re
        staff_match = re.search(r'S00[1-9]', query)
        staff_id = staff_match.group() if staff_match else None
        
        if not staff_id:
            return {
                "intent": "specific_staff",
                "status": "error",
                "error": "No staff ID found in query"
            }
        
        staff = self.data_provider.get_staff_member(staff_id)
        if not staff:
            return {
                "intent": "specific_staff",
                "status": "error",
                "error": f"Staff {staff_id} not found"
            }
        
        attendance = self.analytics.calculate_attendance_metrics(staff_id=staff_id)
        productivity = self.analytics.calculate_productivity(staff_id=staff_id)
        
        response = {
            "intent": "specific_staff",
            "status": "success",
            "summary": f"Analysis for {staff.get('staff_name', staff_id)}",
            "data": {
                "staff": staff,
                "attendance": attendance,
                "productivity": productivity
            },
            "insights": [],
            "recommendations": [],
            "requires_approval": False
        }
        
        return response
    
    def _handle_action_proposal(self, query: str) -> Dict[str, Any]:
        """Handle action proposals (requires approval)"""
        response = {
            "intent": "action_proposal",
            "status": "PENDING_APPROVAL",
            "summary": "Action proposal requires Human Head approval",
            "data": {
                "proposed_action": query,
                "timestamp": datetime.now().isoformat(),
                "status": "PENDING_APPROVAL"
            },
            "insights": [],
            "recommendations": [],
            "requires_approval": True,
            "message": "This action requires Human Head approval."
        }
        
        # Store pending action
        self.pending_actions.append({
            "id": len(self.pending_actions) + 1,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "status": "PENDING_APPROVAL"
        })
        
        return response
    
    def _handle_general_query(self) -> Dict[str, Any]:
        """Handle general inquiries"""
        # Get some basic metrics
        attendance = self.analytics.calculate_attendance_metrics()
        productivity = self.analytics.calculate_productivity()
        staffing = self.analytics.analyze_staffing_levels()
        anomalies = self.analytics.detect_anomalies()
        
        response = {
            "intent": "general_inquiry",
            "status": "success",
            "summary": "Workforce Overview",
            "data": {
                "attendance_rate": attendance.get('attendance_rate', 0),
                "avg_productivity": productivity.get('avg_productivity_score', 0),
                "staffing_levels": staffing,
                "anomalies": len(anomalies)
            },
            "insights": [],
            "recommendations": [],
            "requires_approval": False
        }
        
        # Add some insights
        if attendance.get('attendance_rate', 100) < 85:
            response['insights'].append("Attendance is below target")
        
        if productivity.get('avg_productivity_score', 1) < 0.6:
            response['insights'].append("Productivity is below target")
        
        return response
    
    def approve_action(self, action_id: int) -> Dict[str, Any]:
        """Approve a pending action"""
        for action in self.pending_actions:
            if action['id'] == action_id:
                action['status'] = 'APPROVED'
                self.approved_actions.append(action)
                self.pending_actions.remove(action)
                return {
                    "status": "approved",
                    "action": action,
                    "message": "Action approved by Human Head"
                }
        
        return {"status": "error", "error": "Action not found"}
    
    def reject_action(self, action_id: int) -> Dict[str, Any]:
        """Reject a pending action"""
        for action in self.pending_actions:
            if action['id'] == action_id:
                action['status'] = 'REJECTED'
                self.rejected_actions.append(action)
                self.pending_actions.remove(action)
                return {
                    "status": "rejected",
                    "action": action,
                    "message": "Action rejected by Human Head"
                }
        
        return {"status": "error", "error": "Action not found"}
    
    def get_pending_actions(self) -> List[Dict]:
        """Get all pending actions"""
        return self.pending_actions