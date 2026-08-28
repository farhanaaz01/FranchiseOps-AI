"""
LLM Interface for natural language processing.
Uses Google Gemini API with fallback to keyword-based detection.
"""

import logging
import os
from typing import Optional, Dict, Any
import json

from ..config.settings import settings

logger = logging.getLogger(__name__)


class LLMInterface:
    """
    Interface for LLM-based natural language understanding.
    """
    
    def __init__(self):
        """Initialize the LLM interface."""
        self.enabled = False
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the LLM provider."""
        if not settings.has_api_key:
            logger.warning("No API key found. LLM features disabled.")
            return
        
        try:
            # Try to import and initialize Gemini using the new API
            import google.generativeai as genai
            
            # Configure with API key
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            
            # List available models to find a working one
            models = genai.list_models()
            available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
            
            # Try a few models in order of preference
            preferred_models = [
                'models/gemini-1.5-flash',
                'models/gemini-1.5-pro',
                'models/gemini-pro',
                'models/gemini-1.0-pro'
            ]
            
            model_name = None
            for preferred in preferred_models:
                if preferred in available_models or any(preferred in m for m in available_models):
                    model_name = preferred
                    break
            
            if not model_name and available_models:
                model_name = available_models[0]  # Use first available
            
            if model_name:
                self.model = genai.GenerativeModel(model_name)
                self.enabled = True
                logger.info(f"Gemini initialized with model: {model_name}")
            else:
                logger.warning("No suitable Gemini model found. LLM features disabled.")
                
        except ImportError:
            logger.warning("google.generativeai not installed. LLM features disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
    
    def detect_intent(self, query: str) -> Dict[str, Any]:
        """
        Detect intent from a natural language query.
        
        Args:
            query: The user's query
        
        Returns:
            Dict with intent and extracted entities
        """
        if not self.enabled or not self.model:
            # Fallback: basic intent detection
            return self._fallback_intent_detection(query)
        
        try:
            # Create a prompt for intent detection
            prompt = f"""
            Analyze the following inventory-related query and extract:
            1. Intent (inventory_status, shortage_detection, stockout_prediction, replenishment, wastage_analysis, overstock_detection, purchase_action, approval)
            2. Item name or ID if mentioned
            3. Outlet ID if mentioned
            4. Any other relevant entities
            
            Query: "{query}"
            
            Return the result as a JSON object with keys: 'intent', 'entities'.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response
            try:
                result = json.loads(response.text.strip())
                return result
            except json.JSONDecodeError:
                # Try to extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
                return self._fallback_intent_detection(query)
                
        except Exception as e:
            logger.error(f"Gemini intent detection failed: {e}")
            return self._fallback_intent_detection(query)
    
    def _fallback_intent_detection(self, query: str) -> Dict[str, Any]:
        """Fallback intent detection using keywords."""
        query_lower = query.lower()
        
        # Extract entities
        entities = {}
        
        # Check for item names (common items)
        common_items = {
            'milk': 'ITEM001',
            'bread': 'ITEM002',
            'eggs': 'ITEM003',
            'butter': 'ITEM004',
            'sugar': 'ITEM005',
            'flour': 'ITEM006',
            'oil': 'ITEM007',
            'tomatoes': 'ITEM008'
        }
        
        for name, item_id in common_items.items():
            if name in query_lower:
                entities['item_name'] = name.capitalize()
                entities['item_id'] = item_id
                break
        
        # Check for outlet
        import re
        outlet_match = re.search(r'OUT[0-9]{3}', query.upper())
        if outlet_match:
            entities['outlet_id'] = outlet_match.group()
        
        # Detect intent
        intent = 'inventory_status'
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
        elif any(word in query_lower for word in ['place', 'execute', 'action']):
            intent = 'purchase_action'
        
        return {'intent': intent, 'entities': entities}