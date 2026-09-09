import os
import json
import logging
from typing import Dict, Any, Optional, List

# Handle both old and new Google AI packages
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logging.warning("google.generativeai not available. Using fallback mode.")

logger = logging.getLogger(__name__)

class LLMInterface:
    def __init__(self, model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name
        self.available = False
        
        if self.api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                # Use a simpler model name that's guaranteed to work
                self.model = genai.GenerativeModel('gemini-pro')
                # Test the model with a simple query
                try:
                    response = self.model.generate_content("Test")
                    self.available = True
                    logger.info(f"Using Gemini LLM interface with model: gemini-pro")
                except Exception as e:
                    logger.warning(f"Gemini model test failed: {e}. Using fallback mode.")
                    self.available = False
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}. Using fallback mode.")
                self.available = False
        else:
            if not self.api_key:
                logger.warning("No API key found. Using fallback mode.")
            if not GENAI_AVAILABLE:
                logger.warning("google.generativeai package not installed. Using fallback mode.")
            self.available = False
            
    def detect_intent(self, query: str) -> Dict[str, Any]:
        """Detect intent from natural language query"""
        if self.available:
            try:
                prompt = f"""
                Analyze the following marketing query and determine the intent.
                Return ONLY a JSON object with these exact keys: intent, parameters, confidence.
                
                Intents must be one of: 
                campaign_performance, campaign_comparison, engagement_analysis, roi_analysis, 
                promotion_effectiveness, underperforming, successful, trends, recommendations, 
                proposed_action, general
                
                Query: {query}
                
                Return JSON format:
                {{"intent": "campaign_performance", "parameters": {{}}, "confidence": 0.8}}
                """
                
                response = self.model.generate_content(prompt)
                result = self._parse_json_response(response.text)
                return result
            except Exception as e:
                logger.error(f"Intent detection failed: {e}")
                return self._fallback_intent_detection(query)
        else:
            return self._fallback_intent_detection(query)
            
    def _fallback_intent_detection(self, query: str) -> Dict[str, Any]:
        """Fallback rule-based intent detection"""
        query_lower = query.lower()
        
        # Campaign performance
        if any(word in query_lower for word in ['performance', 'perform', 'how are', 'how is', 'status']):
            return {'intent': 'campaign_performance', 'parameters': {}, 'confidence': 0.7}
        # Campaign comparison
        elif any(word in query_lower for word in ['compare', 'best', 'highest', 'top', 'better']):
            return {'intent': 'campaign_comparison', 'parameters': {}, 'confidence': 0.7}
        # Engagement analysis
        elif any(word in query_lower for word in ['engagement', 'interact', 'like', 'share', 'comment']):
            return {'intent': 'engagement_analysis', 'parameters': {}, 'confidence': 0.7}
        # ROI analysis
        elif any(word in query_lower for word in ['roi', 'return', 'investment']):
            return {'intent': 'roi_analysis', 'parameters': {}, 'confidence': 0.7}
        # Promotion effectiveness
        elif any(word in query_lower for word in ['promotion', 'discount', 'offer']):
            return {'intent': 'promotion_effectiveness', 'parameters': {}, 'confidence': 0.7}
        # Underperforming
        elif any(word in query_lower for word in ['underperforming', 'poor', 'bad', 'low', 'worst']):
            return {'intent': 'underperforming', 'parameters': {}, 'confidence': 0.7}
        # Successful
        elif any(word in query_lower for word in ['successful', 'best', 'high', 'good', 'great']):
            return {'intent': 'successful', 'parameters': {}, 'confidence': 0.7}
        # Trends
        elif any(word in query_lower for word in ['trend', 'change', 'increase', 'decrease', 'growing']):
            return {'intent': 'trends', 'parameters': {}, 'confidence': 0.7}
        # Recommendations
        elif any(word in query_lower for word in ['recommend', 'suggest', 'improve', 'advice']):
            return {'intent': 'recommendations', 'parameters': {}, 'confidence': 0.7}
        # Proposed action
        elif any(word in query_lower for word in ['increase budget', 'increase spend', 'launch', 'create campaign']):
            return {'intent': 'proposed_action', 'parameters': {}, 'confidence': 0.7}
        else:
            return {'intent': 'general', 'parameters': {}, 'confidence': 0.5}
            
    def generate_response(self, context: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Generate response using LLM"""
        if self.available:
            try:
                # Limit context size to avoid token limits
                context_str = json.dumps(context, indent=2)[:2000]
                prompt = f"""
                Based on the following marketing analysis, generate a natural language response.
                
                Analysis: {context_str}
                User Query: {query}
                
                Provide a clear, concise, and actionable response.
                """
                
                response = self.model.generate_content(prompt)
                return {
                    'response': response.text,
                    'source': 'gemini'
                }
            except Exception as e:
                logger.error(f"Response generation failed: {e}")
                return {
                    'response': f"Analysis complete. Here are the key insights from the marketing data.",
                    'source': 'fallback'
                }
        else:
            return {
                'response': f"Analysis complete. Here are the key insights from the marketing data.",
                'source': 'fallback'
            }
            
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            # Find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
        except:
            pass
        return {'intent': 'general', 'parameters': {}, 'confidence': 0.5}