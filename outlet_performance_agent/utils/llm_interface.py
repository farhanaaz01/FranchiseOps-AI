"""
LLM Interface for the Outlet Performance Agent
Supports Google Gemini with fallback to mock mode
"""
import os
import json
import logging
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Try to import Gemini, but handle gracefully if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    import logging
    logging.warning("google.generativeai not available. Using mock LLM.")

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class LLMInterface(ABC):
    """Abstract interface for LLM interactions"""
    
    @abstractmethod
    def detect_intent(self, query: str) -> str:
        """Detect the intent of a user query"""
        pass
    
    @abstractmethod
    def generate_insights(self, data: Any) -> Optional[str]:
        """Generate natural language insights from data"""
        pass
    
    @abstractmethod
    def generate_recommendations(self, data: Any) -> Optional[str]:
        """Generate recommendations based on data"""
        pass
    
    @abstractmethod
    def explain_analysis(self, analysis: Dict[str, Any]) -> str:
        """Generate a natural language explanation of analysis"""
        pass


class GeminiLLMInterface(LLMInterface):
    """Google Gemini implementation"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        """
        Initialize Gemini interface
        
        Args:
            api_key: Google API key (or from environment)
            model_name: Model to use (gemini-pro is the free tier)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            logger.warning("No API key provided for Gemini. Falling back to mock mode.")
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        if not GEMINI_AVAILABLE:
            logger.warning("google.generativeai package not available. Falling back to mock.")
            raise ImportError("google.generativeai not installed")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Try different model names
        model_names = ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
        self.model = None
        
        for name in model_names:
            try:
                self.model = genai.GenerativeModel(name)
                self.model_name = name
                logger.info(f"Gemini initialized with model: {name}")
                break
            except Exception as e:
                logger.debug(f"Model {name} not available: {e}")
                continue
        
        if not self.model:
            raise ValueError("No available Gemini model found")
    
    def detect_intent(self, query: str) -> str:
        """Detect intent using Gemini"""
        try:
            prompt = f"""
            Analyze this query about outlet performance and classify the intent.
            Choose from: underperforming_outlets, outlet_comparison, outlet_performance, 
            health_score, recommendations, proposed_action, clarification, unknown
            
            Query: {query}
            
            Return only the intent classification.
            """
            
            response = self.model.generate_content(prompt)
            intent = response.text.strip().lower()
            
            # Validate intent
            valid_intents = ["underperforming_outlets", "outlet_comparison", "outlet_performance", 
                           "health_score", "recommendations", "proposed_action", "clarification", "unknown"]
            
            if intent not in valid_intents:
                return "unknown"
            
            return intent
            
        except Exception as e:
            logger.error(f"Gemini intent detection failed: {e}")
            return "unknown"
    
    def generate_insights(self, data: Any) -> Optional[str]:
        """Generate insights using Gemini"""
        try:
            # Handle different data types
            if isinstance(data, list) and data and hasattr(data[0], 'dict'):
                data = [item.dict() for item in data]
            
            # Limit data size
            data_str = json.dumps(data, default=str)
            if len(data_str) > 2000:
                data_str = data_str[:2000] + "..."
            
            prompt = f"""
            Based on the following performance data, generate 2-3 key insights:
            
            Data: {data_str}
            
            Focus on meaningful patterns and notable findings.
            Be concise and actionable.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini insight generation failed: {e}")
            return None
    
    def generate_recommendations(self, data: Any) -> Optional[str]:
        """Generate recommendations using Gemini"""
        try:
            # Handle different data types
            if isinstance(data, list) and data and hasattr(data[0], 'dict'):
                data = [item.dict() for item in data]
            
            # Limit data size
            data_str = json.dumps(data, default=str)
            if len(data_str) > 2000:
                data_str = data_str[:2000] + "..."
            
            prompt = f"""
            Based on the following performance data, generate actionable recommendations:
            
            Data: {data_str}
            
            Provide specific, actionable recommendations.
            Focus on improving performance.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini recommendation generation failed: {e}")
            return None
    
    def explain_analysis(self, analysis: Dict[str, Any]) -> str:
        """Explain analysis results using Gemini"""
        try:
            prompt = f"""
            Explain these analysis results in clear, natural language:
            
            Analysis: {json.dumps(analysis, default=str)}
            
            Provide a clear explanation that a business owner would understand.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini explanation generation failed: {e}")
            return "Unable to generate explanation."


class MockLLMInterface(LLMInterface):
    """Mock LLM for testing and fallback"""
    
    def detect_intent(self, query: str) -> str:
        """Simple rule-based intent detection"""
        query_lower = query.lower()
        
        # Priority: Check for action requests first
        action_keywords = ["increase", "change", "action", "budget", "spend", "invest", 
                          "promotional", "marketing", "advertising", "campaign", "promote"]
        if any(word in query_lower for word in action_keywords):
            return "proposed_action"
        
        # Check for underperforming
        underperform_keywords = ["underperforming", "poorly", "bad", "worst", "weak", 
                                "declining", "decreasing", "down", "low", "badly", "failing"]
        if any(word in query_lower for word in underperform_keywords):
            return "underperforming_outlets"
        
        # Check for comparison
        compare_keywords = ["compare", "comparison", "versus", "vs", "better", "worse",
                           "top", "best", "worst", "ranking", "rank", "highest", "lowest"]
        if any(word in query_lower for word in compare_keywords):
            return "outlet_comparison"
        
        # Check for recommendations
        rec_keywords = ["recommend", "suggestion", "improve", "advice", "help", "fix", "resolve", 
                       "what should", "how to", "improvement"]
        if any(word in query_lower for word in rec_keywords):
            return "recommendations"
        
        # Check for health score
        health_keywords = ["health", "score", "rating", "healthscore", "health score"]
        if any(word in query_lower for word in health_keywords):
            return "health_score"
        
        # Check for performance
        perf_keywords = ["performance", "revenue", "sales", "doing", "how", "progress",
                        "results", "outlets", "outlet", "perform", "performing"]
        if any(word in query_lower for word in perf_keywords):
            return "outlet_performance"
        
        # Check for outlet IDs
        import re
        if re.search(r'OUT-\d{3}', query.upper()):
            return "outlet_performance"
        
        return "unknown"
    
    def generate_insights(self, data: Any) -> Optional[str]:
        """Generate mock insights"""
        try:
            if isinstance(data, list):
                if data:
                    if isinstance(data[0], dict):
                        total = len(data)
                        # Try to find best and worst
                        best = None
                        worst = None
                        for item in data:
                            if 'outlet_name' in item and 'value' in item:
                                if best is None or item['value'] > best['value']:
                                    best = item
                                if worst is None or item['value'] < worst['value']:
                                    worst = item
                        
                        insights = []
                        if best:
                            insights.append(f"Best performer: {best.get('outlet_name', best.get('outlet_id'))} with value {best.get('value', 0):.2f}")
                        if worst and worst != best:
                            insights.append(f"Worst performer: {worst.get('outlet_name', worst.get('outlet_id'))} with value {worst.get('value', 0):.2f}")
                        
                        if not insights:
                            insights.append(f"Analysis complete: {total} items reviewed")
                        return " | ".join(insights)
                    elif hasattr(data[0], 'dict'):
                        return f"Analysis complete: {len(data)} items reviewed"
                return "No data to analyze"
            return "Performance data available for review"
        except Exception as e:
            return f"Analysis complete"
    
    def generate_recommendations(self, data: Any) -> Optional[str]:
        """Generate mock recommendations"""
        recommendations = []
        
        try:
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        outlet_name = item.get('outlet_name', item.get('outlet_id', 'Outlet'))
                        status = item.get('status', '')
                        if status in ['UNDERPERFORMING', 'AT_RISK', 'CRITICAL']:
                            recommendations.append(f"For {outlet_name}: Review operations and implement improvement plan")
                        elif item.get('trend') == 'decreasing':
                            recommendations.append(f"For {outlet_name}: Investigate causes of decline")
                    elif hasattr(item, 'outlet_name') and hasattr(item, 'status'):
                        if item.status in ['UNDERPERFORMING', 'AT_RISK', 'CRITICAL']:
                            recommendations.append(f"For {item.outlet_name}: Review operations and implement improvement plan")
            elif isinstance(data, dict):
                outlet_name = data.get('outlet_name', data.get('outlet_id', 'Outlet'))
                if data.get('status') in ['UNDERPERFORMING', 'AT_RISK', 'CRITICAL']:
                    recommendations.append(f"For {outlet_name}: Conduct detailed performance review")
        except:
            pass
        
        if not recommendations:
            recommendations = ["Review underperforming outlets and implement targeted improvement plans"]
        
        return " | ".join(recommendations[:3])
    
    def explain_analysis(self, analysis: Dict[str, Any]) -> str:
        """Generate mock explanation"""
        try:
            outlet = analysis.get('outlet_name', analysis.get('outlet_id', 'Outlet'))
            score = analysis.get('score', 'N/A')
            category = analysis.get('category', 'N/A')
            return f"Analysis for {outlet}: Health score is {score} ({category}). Review detailed metrics for complete picture."
        except:
            return "Analysis complete. Consider investigating any performance anomalies."


def get_llm_interface(provider: Optional[str] = None) -> Optional[LLMInterface]:
    """
    Factory function to get the appropriate LLM interface
    
    Args:
        provider: 'gemini', 'mock', or None for auto-detection
    
    Returns:
        LLMInterface instance or None if unavailable
    """
    # Check environment variable
    provider = provider or os.getenv("LLM_PROVIDER", "mock").lower()
    
    # If explicitly set to mock, use mock
    if provider == "mock":
        logger.info("Using mock LLM interface (as configured)")
        return MockLLMInterface()
    
    # Try Gemini if requested
    if provider == "gemini":
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning("GOOGLE_API_KEY not set, falling back to mock")
                return MockLLMInterface()
            
            if not GEMINI_AVAILABLE:
                logger.warning("google.generativeai not installed, falling back to mock")
                return MockLLMInterface()
            
            logger.info("Attempting to initialize Gemini LLM interface...")
            gemini = GeminiLLMInterface(api_key=api_key)
            logger.info("Gemini LLM interface initialized successfully")
            return gemini
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            logger.info("Falling back to mock LLM interface")
            return MockLLMInterface()
    
    # Default: use mock
    logger.info("Using mock LLM interface (default)")
    return MockLLMInterface()