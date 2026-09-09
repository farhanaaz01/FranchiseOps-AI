"""
Staff Agent LLM Interface - Fixed for Gemini API
Uses the new google-genai SDK with proper error handling
"""

import json
import logging
from typing import Dict, Any, Optional

# Try importing the new SDK
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️ google-genai not installed. Run: pip install google-genai")

logger = logging.getLogger(__name__)

class LLMInterface:
    """Interface for LLM operations using Google's GenAI SDK"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.client = None
        self.available = False
        self._tested_models = []
        
        if not GENAI_AVAILABLE:
            logger.warning("google-genai not available - using fallback")
            return
        
        if not api_key:
            logger.warning("No API key provided - using fallback")
            return
        
        # Try to initialize with the provided model
        self._try_init_model(model)
        
        # If that fails, try alternative model names
        if not self.available:
            alternative_models = [
                "gemini-1.5-flash-001",
                "gemini-1.5-pro",
                "gemini-1.0-pro",
                "gemini-1.0-pro-001"
            ]
            for alt_model in alternative_models:
                if self._try_init_model(alt_model):
                    self.model = alt_model
                    break
        
        if not self.available:
            logger.warning("No Gemini models available - using fallback")
    
    def _try_init_model(self, model_name: str) -> bool:
        """Try to initialize a specific model"""
        try:
            self.client = genai.Client(api_key=self.api_key)
            # Test the model with a simple request
            test_response = self.client.models.generate_content(
                model=model_name,
                contents="Test"
            )
            if test_response and test_response.text:
                self.available = True
                self.model = model_name
                logger.info(f"Gemini initialized with model: {model_name}")
                return True
        except Exception as e:
            logger.debug(f"Model {model_name} not available: {e}")
            return False
    
    def detect_intent(self, query: str) -> Dict[str, Any]:
        """Detect intent from user query"""
        if not self.available:
            return self._fallback_intent_detection(query)
        
        try:
            prompt = f"""Analyze this workforce management query and determine the intent.

Query: "{query}"

Classify the intent as exactly one of these types:
- general_inquiry: General questions about workforce
- attendance_analysis: Questions about attendance
- productivity_analysis: Questions about productivity
- staffing_levels: Questions about staffing
- shortage_detection: Questions about understaffing
- overtime_analysis: Questions about overtime
- anomaly_detection: Questions about unusual patterns
- performance_comparison: Questions comparing staff/outlets
- recommendations: Asking for recommendations
- forecasting: Questions about future staffing needs
- specific_staff: Questions about a specific employee
- specific_outlet: Questions about a specific outlet
- action_proposal: Asking to take action (hire, fire, etc.)

Return ONLY JSON with:
{{
    "intent": "the_intent_type",
    "entity": "specific name or ID if mentioned, otherwise null",
    "confidence": 0.0-1.0
}}"""

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if not response or not response.text:
                return self._fallback_intent_detection(query)
            
            result = response.text.strip()
            # Clean markdown if present
            if result.startswith('```json'):
                result = result.replace('```json', '').replace('```', '').strip()
            elif result.startswith('```'):
                result = result.replace('```', '').strip()
            
            parsed = json.loads(result)
            
            # Check for action proposals that need approval
            if parsed.get('intent') in ['action_proposal']:
                parsed['requires_approval'] = True
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return self._fallback_intent_detection(query)
        except Exception as e:
            logger.error(f"Gemini intent detection failed: {e}")
            return self._fallback_intent_detection(query)
    
    def _fallback_intent_detection(self, query: str) -> Dict[str, Any]:
        """Fallback intent detection without LLM - Enhanced version"""
        query_lower = query.lower()
        
        # Check for action proposals first (these require approval)
        action_keywords = ['hire', 'fire', 'suspend', 'salary', 'bonus', 'overtime', 
                          'terminate', 'dismiss', 'remove', 'add staff', 'reduce staff',
                          'increase salary', 'decrease salary', 'promote', 'demote']
        if any(word in query_lower for word in action_keywords):
            return {
                "intent": "action_proposal",
                "entity": None,
                "confidence": 0.8,
                "requires_approval": True
            }
        
        # Attendance keywords
        if any(word in query_lower for word in ['attendance', 'absent', 'late', 'present', 'showed up']):
            return {"intent": "attendance_analysis", "entity": None, "confidence": 0.8}
        
        # Productivity keywords
        if any(word in query_lower for word in ['productivity', 'performance', 'tasks', 'efficiency']):
            return {"intent": "productivity_analysis", "entity": None, "confidence": 0.8}
        
        # Staffing shortage keywords
        if any(word in query_lower for word in ['understaff', 'shortage', 'need more', 'not enough']):
            return {"intent": "shortage_detection", "entity": None, "confidence": 0.8}
        
        # Comparison keywords
        if any(word in query_lower for word in ['compare', 'vs', 'versus', 'better', 'worse']):
            return {"intent": "performance_comparison", "entity": None, "confidence": 0.7}
        
        # Forecasting keywords
        if any(word in query_lower for word in ['forecast', 'predict', 'future', 'next week', 'tomorrow']):
            return {"intent": "forecasting", "entity": None, "confidence": 0.7}
        
        # Overtime keywords
        if any(word in query_lower for word in ['overtime', 'over time', 'extra hours']):
            return {"intent": "overtime_analysis", "entity": None, "confidence": 0.8}
        
        # Anomaly keywords
        if any(word in query_lower for word in ['anomaly', 'unusual', 'strange', 'abnormal']):
            return {"intent": "anomaly_detection", "entity": None, "confidence": 0.7}
        
        # Specific staff
        import re
        staff_match = re.search(r'[sS]00[1-9]', query_lower)
        if staff_match:
            return {"intent": "specific_staff", "entity": staff_match.group().upper(), "confidence": 0.9}
        
        # Specific outlet
        outlet_match = re.search(r'out00[1-9]', query_lower)
        if outlet_match:
            return {"intent": "specific_outlet", "entity": outlet_match.group().upper(), "confidence": 0.9}
        
        # Default
        return {"intent": "general_inquiry", "entity": None, "confidence": 0.5}
    
    def generate_insights(self, data: Dict[str, Any], query: str = None) -> str:
        """Generate natural language insights from data"""
        if not self.available:
            return self._generate_fallback_insights(data)
        
        try:
            # Truncate data for prompt
            data_str = json.dumps(data, indent=2, default=str)
            if len(data_str) > 8000:
                data_str = data_str[:8000] + "... (truncated)"
            
            prompt = f"""Generate a natural language response based on this workforce data.

Query: {query if query else "Provide workforce insights"}

Data:
{data_str}

Provide a clear, professional response that:
1. Summarizes the key findings
2. Highlights any important issues
3. If applicable, suggests recommendations
4. Is conversational and easy to understand

Important: If this involves any action (hiring, firing, salary changes), clearly state that Human Head approval is required.

Response:"""

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                return self._generate_fallback_insights(data)
            
        except Exception as e:
            logger.error(f"Gemini insight generation failed: {e}")
            return self._generate_fallback_insights(data)
    
    def _generate_fallback_insights(self, data: Dict[str, Any]) -> str:
        """Fallback insight generation without LLM - Enhanced version"""
        response_parts = []
        
        # Attendance insights
        if 'attendance_rate' in data:
            rate = data['attendance_rate']
            if rate >= 90:
                response_parts.append(f"✅ Attendance rate is good at {rate}%")
            elif rate >= 80:
                response_parts.append(f"📊 Attendance rate is {rate}% - acceptable but could improve")
            else:
                response_parts.append(f"⚠️ Attendance rate is low at {rate}% - recommend review")
        
        if 'late_days' in data and data.get('late_days', 0) > 10:
            response_parts.append(f"⚠️ High number of late arrivals: {data['late_days']} instances")
        
        if 'absent_days' in data and data.get('absent_days', 0) > 5:
            response_parts.append(f"⚠️ High absenteeism: {data['absent_days']} absences detected")
        
        # Productivity insights
        if 'avg_productivity_score' in data:
            score = data['avg_productivity_score']
            if score >= 0.8:
                response_parts.append(f"✅ Productivity is strong at {score}")
            elif score >= 0.6:
                response_parts.append(f"📊 Productivity is average at {score}")
            else:
                response_parts.append(f"⚠️ Productivity is low at {score} - recommend review")
        
        if 'trend' in data:
            if data['trend'] == 'increasing':
                response_parts.append(f"✅ Productivity is increasing ({data.get('trend_percentage', 0)}%)")
            elif data['trend'] == 'decreasing':
                response_parts.append(f"⚠️ Productivity is declining ({data.get('trend_percentage', 0)}%) - review needed")
        
        # Staffing insights
        if 'staffing_levels' in data:
            understaffed = []
            overstaffed = []
            for outlet, info in data['staffing_levels'].items():
                if info.get('shortage', 0) > 0:
                    understaffed.append(f"{outlet} (need {info['shortage']} more)")
                if info.get('overstaffed', 0) > 0:
                    overstaffed.append(f"{outlet} ({info['overstaffed']} extra)")
            
            if understaffed:
                response_parts.append(f"⚠️ Staffing shortages at: {', '.join(understaffed)}")
                response_parts.append("🔒 This requires Human Head approval to address")
            
            if overstaffed:
                response_parts.append(f"📊 Overstaffing at: {', '.join(overstaffed)} - consider schedule optimization")
        
        # Anomaly insights
        if 'anomalies' in data:
            count = data['anomalies']
            if count > 0:
                response_parts.append(f"⚠️ {count} workforce anomalies detected - recommend review")
                if isinstance(data.get('anomaly_details'), list):
                    for anomaly in data['anomaly_details'][:3]:
                        response_parts.append(f"  • {anomaly}")
        
        # Overtime insights
        if 'total_overtime' in data:
            total = data['total_overtime']
            if total > 0:
                response_parts.append(f"📊 Total overtime: {total} hours")
                if total > 40:
                    response_parts.append("⚠️ High overtime - review workload distribution")
        
        # If no insights generated
        if not response_parts:
            response_parts.append("📊 Analysis complete. No significant issues detected.")
        
        return "\n".join(response_parts)
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations based on analysis - Enhanced version"""
        recommendations = []
        requires_approval = False
        
        # Check for staffing shortages
        if 'staffing_levels' in analysis:
            for outlet, data in analysis['staffing_levels'].items():
                if data.get('shortage', 0) > 2:  # More than 2 staff shortage
                    recommendations.append({
                        "finding": f"Critical staff shortage at {outlet}",
                        "recommendation": f"Immediately hire {data['shortage']} additional staff or adjust schedules",
                        "requires_approval": True,
                        "proposed_action": f"Add {data['shortage']} staff to {outlet}",
                        "priority": "HIGH"
                    })
                    requires_approval = True
                elif data.get('shortage', 0) > 0:
                    recommendations.append({
                        "finding": f"Staff shortage at {outlet}",
                        "recommendation": f"Consider hiring {data['shortage']} additional staff",
                        "requires_approval": True,
                        "proposed_action": f"Add {data['shortage']} staff to {outlet}",
                        "priority": "MEDIUM"
                    })
                    requires_approval = True
        
        # Check for attendance issues
        if 'attendance_metrics' in analysis:
            for staff, data in analysis['attendance_metrics'].items():
                if data.get('attendance_rate', 100) < 70:
                    recommendations.append({
                        "finding": f"Critical attendance issue for {staff}",
                        "recommendation": "Immediate review and intervention required",
                        "requires_approval": True,
                        "proposed_action": f"Review {staff}'s attendance",
                        "priority": "HIGH"
                    })
                    requires_approval = True
                elif data.get('attendance_rate', 100) < 80:
                    recommendations.append({
                        "finding": f"Low attendance for {staff}: {data['attendance_rate']}%",
                        "recommendation": "Review attendance patterns and discuss with employee",
                        "requires_approval": False,
                        "proposed_action": None,
                        "priority": "MEDIUM"
                    })
        
        # Check for performance issues
        if 'performance_metrics' in analysis:
            for staff, data in analysis['performance_metrics'].items():
                if data.get('avg_productivity_score', 1) < 0.4:
                    recommendations.append({
                        "finding": f"Critical performance issue for {staff}",
                        "recommendation": "Immediate performance review required",
                        "requires_approval": True,
                        "proposed_action": f"Review {staff}'s performance",
                        "priority": "HIGH"
                    })
                    requires_approval = True
                elif data.get('avg_productivity_score', 1) < 0.6:
                    recommendations.append({
                        "finding": f"Low productivity for {staff}: {data['avg_productivity_score']}",
                        "recommendation": "Review workload and consider additional training",
                        "requires_approval": False,
                        "proposed_action": None,
                        "priority": "MEDIUM"
                    })
        
        # Check anomalies
        if 'anomalies' in analysis and analysis['anomalies']:
            for anomaly in analysis['anomalies']:
                if anomaly.get('severity') == 'High':
                    recommendations.append({
                        "finding": f"High severity anomaly: {anomaly['type']} for {anomaly.get('staff_id', 'unknown')}",
                        "recommendation": "Immediate review recommended by Human Head",
                        "requires_approval": True,
                        "proposed_action": f"Review {anomaly.get('staff_id', 'staff')} for {anomaly['type']}",
                        "priority": "HIGH"
                    })
                    requires_approval = True
                else:
                    recommendations.append({
                        "finding": f"Anomaly detected: {anomaly['type']} for {anomaly.get('staff_id', 'unknown')}",
                        "recommendation": "Monitor and review if persists",
                        "requires_approval": False,
                        "proposed_action": None,
                        "priority": "LOW"
                    })
        
        # Overtime recommendations
        if 'overtime_analysis' in analysis:
            for staff, data in analysis['overtime_analysis'].items():
                if data.get('total_overtime', 0) > 40:
                    recommendations.append({
                        "finding": f"Excessive overtime for {staff}: {data['total_overtime']} hours",
                        "recommendation": "Urgent review of workload distribution required",
                        "requires_approval": True,
                        "proposed_action": f"Review {staff}'s workload",
                        "priority": "HIGH"
                    })
                    requires_approval = True
                elif data.get('total_overtime', 0) > 20:
                    recommendations.append({
                        "finding": f"High overtime for {staff}: {data['total_overtime']} hours",
                        "recommendation": "Review staffing levels and workload distribution",
                        "requires_approval": False,
                        "proposed_action": None,
                        "priority": "MEDIUM"
                    })
        
        return {
            "recommendations": recommendations,
            "requires_approval": requires_approval,
            "total_issues": len(recommendations),
            "high_priority_count": sum(1 for r in recommendations if r.get('priority') == 'HIGH')
        }