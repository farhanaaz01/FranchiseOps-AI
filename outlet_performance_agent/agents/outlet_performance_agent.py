"""
Outlet Performance Agent - Main agent implementation
"""
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta
import json
import os
import re
from pathlib import Path

from ..models.data_models import (
    Outlet, SalesRecord, HealthScore, AgentResponse, 
    ProposedAction, UnderperformingOutlet, OutletPerformance
)
from ..data_access.data_provider import DataProvider, CSVDataProvider
from ..analytics.metrics import (
    RevenueAnalyzer, SalesAnalyzer, TrendAnalyzer, 
    HealthScoreCalculator, OutletComparator
)
from ..utils.llm_interface import LLMInterface, get_llm_interface

logger = logging.getLogger(__name__)


class OutletPerformanceAgent:
    """
    Main Outlet Performance Agent that orchestrates analytics, reasoning, and recommendations
    """
    
    def __init__(self, 
                 data_provider: Optional[DataProvider] = None,
                 health_score_config: Optional[Dict[str, float]] = None,
                 llm_provider: Optional[str] = None):
        """
        Initialize the agent
        
        Args:
            data_provider: Data provider implementation (uses CSVDataProvider if None)
            health_score_config: Configuration for health score weights
            llm_provider: LLM provider to use ('gemini', 'mock', or None for auto-detect)
        """
        self.data_provider = data_provider or CSVDataProvider()
        self.health_calculator = HealthScoreCalculator(**(health_score_config or {}))
        self.llm = get_llm_interface(provider=llm_provider)
        
        # Cache for performance data
        self._outlet_cache = {}
        self._sales_cache = {}
        self._health_cache = {}
        
        # Approval tracking
        self._pending_approvals: List[ProposedAction] = []
        self._approved_actions: List[ProposedAction] = []
        self._rejected_actions: List[ProposedAction] = []
        self._action_counter = 0
        
        logger.info("OutletPerformanceAgent initialized")
    
    def process_query(self, query: str) -> AgentResponse:
        """
        Process a natural language query and return a structured response
        
        Args:
            query: User's natural language query
        
        Returns:
            Structured AgentResponse with analysis and recommendations
        """
        try:
            # If query is empty, ask for clarification
            if not query or query.strip() == "":
                return AgentResponse(
                    intent="clarification",
                    status="needs_clarification",
                    summary="I need more information to help you.",
                    clarification_question="Please ask a question about outlet performance."
                )
            
            # Use LLM to understand intent (if available)
            if self.llm:
                try:
                    intent = self.llm.detect_intent(query)
                    logger.info(f"LLM detected intent: {intent}")
                except Exception as e:
                    logger.error(f"LLM intent detection failed: {e}")
                    intent = "unknown"
                
                # If LLM failed or returned unknown, use enhanced fallback
                if intent == "unknown":
                    intent = self._enhanced_fallback_intent_detection(query)
                    logger.info(f"Fallback detected intent: {intent}")
            else:
                intent = self._enhanced_fallback_intent_detection(query)
                logger.info(f"Detected intent (fallback): {intent}")
            
            # Route to appropriate handler
            if intent == "underperforming_outlets":
                return self._handle_underperforming_detection(query)
            elif intent == "outlet_comparison":
                return self._handle_comparison(query)
            elif intent == "outlet_performance":
                return self._handle_performance_query(query)
            elif intent == "health_score":
                return self._handle_health_score_query(query)
            elif intent == "recommendations":
                return self._handle_recommendation_query(query)
            elif intent == "proposed_action":
                return self._handle_proposed_action(query)
            elif intent == "clarification":
                return self._handle_clarification(query)
            else:
                # Try to extract outlet ID and do performance analysis
                outlet_ids = self._extract_outlet_ids(query)
                if outlet_ids:
                    return self._handle_performance_query(query)
                else:
                    return AgentResponse(
                        intent="unknown",
                        status="error",
                        summary="I couldn't understand your query.",
                        error="Please ask about outlet performance, comparisons, or health scores. Example: 'How are my outlets performing?' or 'Which outlets are underperforming?'"
                    )
                
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return AgentResponse(
                intent="error",
                status="error",
                summary=f"An error occurred while processing your request.",
                error=str(e)
            )
    
    def _enhanced_fallback_intent_detection(self, query: str) -> str:
        """Enhanced fallback intent detection without LLM - more robust"""
        query_lower = query.lower()
        
        # Check for outlet IDs in query
        has_outlet = bool(re.search(r'OUT-\d{3}', query.upper()))
        
        # Check for time periods
        time_keywords = ["today", "this week", "this month", "last month", "quarter", "year", "period"]
        has_time = any(word in query_lower for word in time_keywords)
        
        # Priority 1: Check for action requests (most important)
        action_keywords = ["increase", "change", "action", "budget", "spend", "invest", 
                          "promotional", "marketing", "advertising", "campaign", "promote",
                          "raise", "reduce", "decrease", "cut", "add", "remove"]
        if any(word in query_lower for word in action_keywords):
            # Check if it's asking about what action to take vs proposing an action
            if any(word in query_lower for word in ["what", "should", "suggest", "recommend", "advice"]):
                return "recommendations"
            return "proposed_action"
        
        # Priority 2: Check for underperforming
        underperform_keywords = ["underperforming", "poorly", "bad", "worst", "weak", 
                                "declining", "decreasing", "down", "low", "badly", "failing",
                                "struggling", "problem", "issue", "trouble"]
        if any(word in query_lower for word in underperform_keywords):
            return "underperforming_outlets"
        
        # Priority 3: Check for comparison
        compare_keywords = ["compare", "comparison", "versus", "vs", "better", "worse",
                           "top", "best", "worst", "ranking", "rank", "highest", "lowest",
                           "difference", "gap", "vs", "versus"]
        if any(word in query_lower for word in compare_keywords):
            return "outlet_comparison"
        
        # Priority 4: Check for recommendations
        rec_keywords = ["recommend", "suggestion", "improve", "advice", "help", "fix", "resolve", 
                       "what should", "how to", "improvement", "strategy", "plan", "action"]
        if any(word in query_lower for word in rec_keywords):
            return "recommendations"
        
        # Priority 5: Check for health score
        health_keywords = ["health", "score", "rating", "healthscore", "health score", 
                          "status", "condition", "state"]
        if any(word in query_lower for word in health_keywords):
            return "health_score"
        
        # Priority 6: Check for performance
        perf_keywords = ["performance", "revenue", "sales", "doing", "how", "progress",
                        "results", "outlets", "outlet", "perform", "performing",
                        "metrics", "kpi", "growth", "trend"]
        if any(word in query_lower for word in perf_keywords) or has_outlet:
            return "outlet_performance"
        
        # If we have an outlet ID but nothing else, assume performance query
        if has_outlet:
            return "outlet_performance"
        
        # Check for ambiguous queries
        if any(word in query_lower for word in ["tell me", "show me", "give me"]):
            return "outlet_performance"
        
        # Default: ask for clarification
        return "clarification"
    
    def _handle_clarification(self, query: str) -> AgentResponse:
        """Handle clarification requests"""
        # Try to provide helpful guidance based on query keywords
        if "outlet" in query.lower():
            return AgentResponse(
                intent="clarification",
                status="needs_clarification",
                summary="I need more specific information about which outlets you're interested in.",
                clarification_question="Please specify which outlet(s) you want to analyze. You can use outlet IDs like OUT-101, OUT-102, etc."
            )
        elif "time" in query.lower() or "period" in query.lower():
            return AgentResponse(
                intent="clarification",
                status="needs_clarification",
                summary="I need to know what time period you're interested in.",
                clarification_question="Please specify a time period (e.g., 'this month', 'last quarter', 'last 90 days')."
            )
        else:
            return AgentResponse(
                intent="clarification",
                status="needs_clarification",
                summary="I need more information to help you.",
                clarification_question="Please ask a specific question about outlet performance. Examples: 'How are my outlets performing?', 'Which outlets are underperforming?', 'Compare OUT-101 and OUT-102'"
            )
    
    def _handle_performance_query(self, query: str) -> AgentResponse:
        """Handle general performance query"""
        try:
            # Extract outlet IDs if mentioned
            outlet_ids = self._extract_outlet_ids(query)
            
            # Determine time period from query
            period = self._extract_time_period(query)
            
            # Get outlets
            if outlet_ids:
                outlets = [o for o in self.data_provider.get_outlets() if o.outlet_id in outlet_ids]
                if not outlets:
                    return AgentResponse(
                        intent="outlet_performance",
                        status="error",
                        summary="No matching outlets found.",
                        error=f"No outlets found with IDs: {', '.join(outlet_ids)}"
                    )
            else:
                outlets = self.data_provider.get_outlets()
            
            if not outlets:
                return AgentResponse(
                    intent="outlet_performance",
                    status="error",
                    summary="No outlets found.",
                    error="No outlets available for analysis."
                )
            
            # Get sales data
            end_date = date.today()
            if period == "week":
                start_date = end_date - timedelta(days=7)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            elif period == "quarter":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=90)  # Default 90 days
            
            all_sales = self.data_provider.get_sales_data(start_date, end_date)
            
            # Group sales by outlet
            sales_by_outlet = {}
            for outlet in outlets:
                outlet_sales = [s for s in all_sales if s.outlet_id == outlet.outlet_id]
                sales_by_outlet[outlet.outlet_id] = outlet_sales
            
            # Analyze each outlet
            performances = []
            for outlet in outlets:
                sales = sales_by_outlet.get(outlet.outlet_id, [])
                perf = self._analyze_single_outlet(outlet, sales, all_outlets=outlets, sales_by_outlet=sales_by_outlet)
                performances.append(perf)
            
            # Sort by health score if available
            performances.sort(key=lambda x: x.health_score.score if x.health_score else 0, reverse=True)
            
            # Generate insights using LLM if available
            insights = []
            recommendations = []
            
            if self.llm:
                try:
                    # Generate natural language insights
                    insight_text = self.llm.generate_insights(performances)
                    if insight_text and insight_text != "No data to analyze":
                        insights.append(insight_text)
                except Exception as e:
                    logger.error(f"LLM insight generation failed: {e}")
            
            # Always generate basic insights as fallback
            basic_insights = self._generate_basic_insights(performances)
            if basic_insights:
                insights.extend(basic_insights)
            
            if self.llm:
                try:
                    # Generate recommendations
                    rec_text = self.llm.generate_recommendations(performances)
                    if rec_text and rec_text != "No data to analyze":
                        recommendations.append(rec_text)
                except Exception as e:
                    logger.error(f"LLM recommendation generation failed: {e}")
            
            # Generate basic recommendations as fallback
            if not recommendations:
                basic_recs = self._generate_basic_recommendations(performances)
                recommendations.extend(basic_recs)
            
            # Create summary
            total_revenue = sum(p.total_revenue for p in performances if p.total_revenue)
            avg_revenue = total_revenue / len(performances) if performances else 0
            
            summary = f"Analyzed {len(performances)} outlets over {period} period. "
            if performances:
                best = performances[0]
                worst = performances[-1]
                summary += f"Best: {best.outlet_name} (score: {best.health_score.score:.1f}/100 if best.health_score else 'N/A'), "
                summary += f"Worst: {worst.outlet_name} (score: {worst.health_score.score:.1f}/100 if worst.health_score else 'N/A')."
            
            return AgentResponse(
                intent="outlet_performance",
                status="success",
                summary=summary,
                data=[p.dict() for p in performances],
                insights=insights[:3] if insights else ["No insights generated"],
                recommendations=recommendations[:3] if recommendations else ["No recommendations available"],
                confidence=0.85
            )
            
        except Exception as e:
            logger.error(f"Performance query failed: {e}", exc_info=True)
            return AgentResponse(
                intent="outlet_performance",
                status="error",
                summary="Failed to analyze performance.",
                error=str(e)
            )
    
    def _handle_underperforming_detection(self, query: str) -> AgentResponse:
        """Handle underperforming outlet detection"""
        try:
            outlets = self.data_provider.get_outlets()
            
            if not outlets:
                return AgentResponse(
                    intent="underperforming_outlets",
                    status="error",
                    summary="No outlets found.",
                    error="No outlets available for analysis."
                )
            
            # Get sales data for last 90 days
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
            all_sales = self.data_provider.get_sales_data(start_date, end_date)
            
            # Group sales by outlet
            sales_by_outlet = {}
            for outlet in outlets:
                outlet_sales = [s for s in all_sales if s.outlet_id == outlet.outlet_id]
                sales_by_outlet[outlet.outlet_id] = outlet_sales
            
            # Calculate health scores and detect underperformance
            underperformers = []
            
            for outlet in outlets:
                sales = sales_by_outlet.get(outlet.outlet_id, [])
                health = self.health_calculator.calculate_health_score(
                    outlet.outlet_id, 
                    sales,
                    outlets,
                    sales_by_outlet
                )
                
                # Check if underperforming
                if health.category in ["UNDERPERFORMING", "AT_RISK", "CRITICAL"]:
                    # Find reasons
                    reasons = self._find_underperformance_reasons(outlet, sales, health)
                    
                    # Determine severity
                    if health.category == "CRITICAL":
                        severity = "critical"
                    elif health.category == "AT_RISK":
                        severity = "high"
                    else:
                        severity = "medium"
                    
                    underperformer = UnderperformingOutlet(
                        outlet_id=outlet.outlet_id,
                        outlet_name=outlet.outlet_name,
                        status=health.category,
                        severity=severity,
                        reasons=reasons,
                        supporting_metrics={
                            "health_score": health.score,
                            "revenue": RevenueAnalyzer.total_revenue(sales) if sales else 0,
                            "trend": TrendAnalyzer.detect_trend(sales) if sales else "unknown",
                            "days_with_data": len(sales)
                        },
                        trend=TrendAnalyzer.detect_trend(sales) if sales else "unknown",
                        confidence=0.85 if sales else 0.5,
                        recommendations=self._generate_outlet_recommendations(outlet, sales, health)
                    )
                    underperformers.append(underperformer)
            
            # Generate response
            if underperformers:
                summary = f"Found {len(underperformers)} underperforming outlets."
                insights = [f"Outlet {u.outlet_id} ({u.outlet_name}) is {u.status.lower()} with {u.severity} severity." 
                           for u in underperformers]
                
                # Get recommendations from LLM if available
                recommendations = []
                if self.llm and underperformers:
                    try:
                        rec_text = self.llm.generate_recommendations([u.dict() for u in underperformers])
                        if rec_text and rec_text != "No data to analyze":
                            recommendations.append(rec_text)
                    except Exception as e:
                        logger.error(f"LLM recommendation generation failed: {e}")
                
                # Add basic recommendations
                basic_recs = self._generate_underperformer_recommendations(underperformers)
                recommendations.extend(basic_recs)
                
                return AgentResponse(
                    intent="underperforming_outlets",
                    status="success",
                    summary=summary,
                    data=[u.dict() for u in underperformers],
                    insights=insights,
                    recommendations=recommendations[:3] if recommendations else ["Review underperforming outlets"],
                    confidence=0.85
                )
            else:
                return AgentResponse(
                    intent="underperforming_outlets",
                    status="success",
                    summary="No underperforming outlets detected.",
                    insights=["All outlets are performing at acceptable levels."],
                    confidence=0.90
                )
                
        except Exception as e:
            logger.error(f"Underperforming detection failed: {e}", exc_info=True)
            return AgentResponse(
                intent="underperforming_outlets",
                status="error",
                summary="Failed to detect underperforming outlets.",
                error=str(e)
            )
    
    def _handle_comparison(self, query: str) -> AgentResponse:
        """Handle outlet comparison queries"""
        try:
            # Extract outlet IDs
            outlet_ids = self._extract_outlet_ids(query)
            
            if not outlet_ids:
                # If no specific outlets, compare all
                outlets = self.data_provider.get_outlets()
                if len(outlets) < 2:
                    return AgentResponse(
                        intent="outlet_comparison",
                        status="error",
                        summary="Need at least 2 outlets to compare.",
                        error="Please specify at least 2 outlet IDs or ensure there are multiple outlets available."
                    )
                outlet_ids = [o.outlet_id for o in outlets]
            
            # Get outlets
            all_outlets = self.data_provider.get_outlets()
            outlets = [o for o in all_outlets if o.outlet_id in outlet_ids]
            
            if len(outlets) < 2:
                return AgentResponse(
                    intent="outlet_comparison",
                    status="error",
                    summary=f"Need at least 2 outlets to compare. Found {len(outlets)}.",
                    error="Please provide at least 2 outlet IDs."
                )
            
            # Get sales data for last 30 days
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            all_sales = self.data_provider.get_sales_data(start_date, end_date, outlet_ids)
            
            # Group by outlet
            sales_by_outlet = {}
            for outlet in outlets:
                outlet_sales = [s for s in all_sales if s.outlet_id == outlet.outlet_id]
                sales_by_outlet[outlet.outlet_id] = outlet_sales
            
            # Compare
            comparison = OutletComparator.compare_outlets(sales_by_outlet, "revenue")
            
            if not comparison:
                return AgentResponse(
                    intent="outlet_comparison",
                    status="error",
                    summary="No data available for comparison.",
                    error="No sales data found for the specified outlets."
                )
            
            # Generate insights
            insights = []
            if len(comparison) >= 2:
                best = comparison[0]
                worst = comparison[-1]
                best_outlet = next((o for o in outlets if o.outlet_id == best['outlet_id']), None)
                worst_outlet = next((o for o in outlets if o.outlet_id == worst['outlet_id']), None)
                
                insights.append(f"Best performer: {best_outlet.outlet_name if best_outlet else best['outlet_id']} with revenue {best['value']:.2f}")
                insights.append(f"Worst performer: {worst_outlet.outlet_name if worst_outlet else worst['outlet_id']} with revenue {worst['value']:.2f}")
                
                # Calculate difference
                if best['value'] > 0:
                    diff = ((best['value'] - worst['value']) / best['value']) * 100
                    insights.append(f"Performance gap: {diff:.1f}% difference between best and worst")
            
            # Get LLM insights if available
            if self.llm:
                try:
                    llm_insight = self.llm.generate_insights(comparison)
                    if llm_insight and llm_insight != "No data to analyze":
                        insights.append(llm_insight)
                except Exception as e:
                    logger.error(f"LLM insight generation failed: {e}")
            
            return AgentResponse(
                intent="outlet_comparison",
                status="success",
                summary=f"Compared {len(outlets)} outlets over the last 30 days.",
                data=comparison,
                insights=insights[:3],
                confidence=0.90
            )
            
        except Exception as e:
            logger.error(f"Comparison failed: {e}", exc_info=True)
            return AgentResponse(
                intent="outlet_comparison",
                status="error",
                summary="Failed to compare outlets.",
                error=str(e)
            )
    
    def _handle_health_score_query(self, query: str) -> AgentResponse:
        """Handle health score queries"""
        try:
            outlet_ids = self._extract_outlet_ids(query)
            
            if not outlet_ids:
                # Check if query mentions "outlet" but no ID
                if "outlet" in query.lower():
                    return AgentResponse(
                        intent="health_score",
                        status="needs_clarification",
                        summary="Which outlet's health score would you like to see?",
                        clarification_question="Please provide an outlet ID like OUT-101 or OUT-104."
                    )
                else:
                    # Show health scores for all outlets
                    outlets = self.data_provider.get_outlets()
                    if not outlets:
                        return AgentResponse(
                            intent="health_score",
                            status="error",
                            summary="No outlets found.",
                            error="No outlets available for analysis."
                        )
                    outlet_ids = [o.outlet_id for o in outlets]
            
            # Get first outlet ID
            outlet_id = outlet_ids[0]
            
            # Get outlet and sales
            outlet = self.data_provider.get_outlet(outlet_id)
            if not outlet:
                return AgentResponse(
                    intent="health_score",
                    status="error",
                    summary="Outlet not found.",
                    error=f"Outlet {outlet_id} not found."
                )
            
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
            sales = self.data_provider.get_outlet_sales(outlet_id, start_date, end_date)
            
            if not sales:
                return AgentResponse(
                    intent="health_score",
                    status="error",
                    summary=f"No sales data found for {outlet.outlet_name}.",
                    error=f"No sales records found for outlet {outlet_id} in the last 90 days."
                )
            
            # Calculate health score
            outlets = self.data_provider.get_outlets()
            all_sales = self.data_provider.get_sales_data(start_date, end_date)
            sales_by_outlet = {}
            for o in outlets:
                sales_by_outlet[o.outlet_id] = [s for s in all_sales if s.outlet_id == o.outlet_id]
            
            health = self.health_calculator.calculate_health_score(
                outlet_id,
                sales,
                outlets,
                sales_by_outlet
            )
            
            # Generate explanation
            explanation = health.explanation
            
            # Try to get LLM explanation
            if self.llm:
                try:
                    llm_explanation = self.llm.explain_analysis(health.dict())
                    if llm_explanation and llm_explanation != "Unable to generate explanation.":
                        explanation = llm_explanation
                except Exception as e:
                    logger.error(f"LLM explanation generation failed: {e}")
            
            return AgentResponse(
                intent="health_score",
                status="success",
                summary=f"Health score for {outlet.outlet_name}: {health.score:.1f}/100 ({health.category})",
                data=[health.dict()],
                insights=[explanation],
                confidence=0.90
            )
            
        except Exception as e:
            logger.error(f"Health score query failed: {e}", exc_info=True)
            return AgentResponse(
                intent="health_score",
                status="error",
                summary="Failed to calculate health score.",
                error=str(e)
            )
    
    def _handle_recommendation_query(self, query: str) -> AgentResponse:
        """Handle recommendation queries"""
        try:
            outlet_ids = self._extract_outlet_ids(query)
            
            if not outlet_ids:
                # If no specific outlet, recommend for all underperformers
                return self._handle_underperforming_detection(query)
            
            # Get data for specific outlet
            outlet = self.data_provider.get_outlet(outlet_ids[0])
            if not outlet:
                return AgentResponse(
                    intent="recommendations",
                    status="error",
                    summary="Outlet not found.",
                    error=f"Outlet {outlet_ids[0]} not found."
                )
            
            end_date = date.today()
            start_date = end_date - timedelta(days=90)
            sales = self.data_provider.get_outlet_sales(outlet_ids[0], start_date, end_date)
            
            if not sales:
                return AgentResponse(
                    intent="recommendations",
                    status="error",
                    summary=f"No sales data found for {outlet.outlet_name}.",
                    error=f"No sales records found for outlet {outlet_ids[0]} in the last 90 days."
                )
            
            # Calculate health
            outlets = self.data_provider.get_outlets()
            all_sales = self.data_provider.get_sales_data(start_date, end_date)
            sales_by_outlet = {}
            for o in outlets:
                sales_by_outlet[o.outlet_id] = [s for s in all_sales if s.outlet_id == o.outlet_id]
            
            health = self.health_calculator.calculate_health_score(
                outlet_ids[0],
                sales,
                outlets,
                sales_by_outlet
            )
            
            # Generate recommendations
            recommendations = self._generate_outlet_recommendations(outlet, sales, health)
            
            # Try to get LLM recommendations
            if self.llm:
                try:
                    data_dict = {
                        "outlet_id": outlet.outlet_id,
                        "outlet_name": outlet.outlet_name,
                        "health_score": health.score,
                        "category": health.category,
                        "revenue": RevenueAnalyzer.total_revenue(sales) if sales else 0,
                        "trend": TrendAnalyzer.detect_trend(sales) if sales else "unknown"
                    }
                    llm_recs = self.llm.generate_recommendations(data_dict)
                    if llm_recs and llm_recs != "No data to analyze":
                        recommendations.append(llm_recs)
                except Exception as e:
                    logger.error(f"LLM recommendation generation failed: {e}")
            
            return AgentResponse(
                intent="recommendations",
                status="success",
                summary=f"Recommendations for {outlet.outlet_name}:",
                recommendations=recommendations[:3],
                data=[{
                    "outlet_id": outlet.outlet_id,
                    "health_score": health.score,
                    "category": health.category
                }],
                confidence=0.80
            )
            
        except Exception as e:
            logger.error(f"Recommendation query failed: {e}", exc_info=True)
            return AgentResponse(
                intent="recommendations",
                status="error",
                summary="Failed to generate recommendations.",
                error=str(e)
            )
    
    def _handle_proposed_action(self, query: str) -> AgentResponse:
        """
        Handle proposed consequential action requiring approval
        This is where human-in-the-loop is enforced
        """
        try:
            # Extract outlet ID
            outlet_ids = self._extract_outlet_ids(query)
            outlet_id = outlet_ids[0] if outlet_ids else "UNKNOWN"
            
            # Get outlet name
            outlet_name = "Unknown Outlet"
            if outlet_id != "UNKNOWN":
                outlet = self.data_provider.get_outlet(outlet_id)
                if outlet:
                    outlet_name = outlet.outlet_name
            
            # Parse action from query
            action_type = "GENERIC_ACTION"
            action_desc = ""
            cost = 0.0
            
            # Parse budget increase
            import re
            budget_match = re.search(r'₹?(\d+[,.]?\d*)\s*[kK]?', query)
            if budget_match:
                try:
                    cost = float(budget_match.group(1).replace(',', ''))
                    if 'k' in query.lower() or 'K' in query:
                        cost *= 1000
                except:
                    cost = 5000.0
            
            # Determine action type
            if "promotional" in query.lower() or "marketing" in query.lower() or "advertising" in query.lower():
                action_type = "INCREASE_PROMOTIONAL_BUDGET"
                action_desc = f"Increase promotional budget by ₹{cost:,.0f} for {outlet_name}"
            elif "staff" in query.lower() or "employee" in query.lower():
                action_type = "INCREASE_STAFF"
                action_desc = f"Increase staffing at {outlet_name}"
            elif "inventory" in query.lower() or "stock" in query.lower():
                action_type = "INCREASE_INVENTORY"
                action_desc = f"Increase inventory at {outlet_name}"
            else:
                action_type = "GENERIC_ACTION"
                action_desc = f"Take action to improve performance at {outlet_name}"
            
            # Generate reason
            reason = "Performance analysis indicates need for intervention."
            if outlet_id != "UNKNOWN":
                end_date = date.today()
                start_date = end_date - timedelta(days=30)
                sales = self.data_provider.get_outlet_sales(outlet_id, start_date, end_date)
                if sales:
                    trend = TrendAnalyzer.detect_trend(sales)
                    if trend == "decreasing":
                        reason = f"Revenue showing decreasing trend at {outlet_name}"
                        if cost > 0:
                            reason += f". Proposed budget increase of ₹{cost:,.0f} to address decline"
                    else:
                        reason = f"Performance metrics indicate need for improvement at {outlet_name}"
            
            # Generate estimated impact
            estimated_impact = "Expected 5-10% performance improvement over next month"
            if cost > 0:
                estimated_impact = f"Expected ROI: {cost * 2:,.0f} - {cost * 3:,.0f} in additional revenue"
            
            # Create proposed action
            proposed_action = ProposedAction(
                action_type=action_type,
                description=action_desc,
                reason=reason,
                cost_estimate=cost if cost > 0 else None,
                estimated_impact=estimated_impact
            )
            
            # Add to pending approvals
            self._pending_approvals.append(proposed_action)
            
            return AgentResponse(
                intent="proposed_action",
                status="pending_approval",
                summary="A consequential action has been proposed and requires human approval.",
                requires_human_approval=True,
                proposed_action=proposed_action,
                insights=[
                    f"This action involves {'spending money' if cost > 0 else 'making operational changes'}.",
                    "Human Head approval is required before execution."
                ],
                warnings=[
                    "This action requires human approval before execution.",
                    "Unapproved actions will not be executed."
                ]
            )
            
        except Exception as e:
            logger.error(f"Proposed action failed: {e}", exc_info=True)
            return AgentResponse(
                intent="proposed_action",
                status="error",
                summary="Failed to propose action.",
                error=str(e)
            )
    
    def approve_action(self, action_id: str, approver: str = "Human Head") -> bool:
        """
        Approve a pending action
        
        Args:
            action_id: ID of the action to approve
            approver: Name/ID of the approver
        
        Returns:
            True if approved, False otherwise
        """
        for action in self._pending_approvals:
            if str(action.created_at) == str(action_id):  # Simplified
                action.status = "APPROVED"
                action.approved_by = approver
                action.approved_at = datetime.now()
                self._approved_actions.append(action)
                self._pending_approvals.remove(action)
                logger.info(f"Action approved by {approver}: {action.description}")
                return True
        
        return False
    
    def reject_action(self, action_id: str) -> bool:
        """Reject a pending action"""
        for action in self._pending_approvals:
            if str(action.created_at) == str(action_id):  # Simplified
                action.status = "REJECTED"
                self._rejected_actions.append(action)
                self._pending_approvals.remove(action)
                logger.info(f"Action rejected: {action.description}")
                return True
        
        return False
    
    def _analyze_single_outlet(self, outlet: Outlet, sales: List[SalesRecord], 
                               all_outlets: List[Outlet] = None, 
                               sales_by_outlet: Dict[str, List[SalesRecord]] = None) -> OutletPerformance:
        """Analyze a single outlet's performance"""
        if not sales:
            return OutletPerformance(
                outlet_id=outlet.outlet_id,
                outlet_name=outlet.outlet_name,
                period="last_90_days",
                total_revenue=0,
                average_revenue=0,
                transaction_count=0,
                average_order_value=0,
                revenue_growth=0,
                trend="unknown",
                health_score=HealthScore(
                    outlet_id=outlet.outlet_id,
                    score=0,
                    category="CRITICAL",
                    explanation="No sales data available"
                )
            )
        
        # Calculate metrics
        total_revenue = RevenueAnalyzer.total_revenue(sales)
        avg_revenue = RevenueAnalyzer.average_revenue(sales)
        transactions = SalesAnalyzer.transaction_count(sales)
        aov = SalesAnalyzer.average_order_value(sales)
        growth = RevenueAnalyzer.revenue_growth(sales)
        trend = TrendAnalyzer.detect_trend(sales)
        
        # Calculate health score
        if all_outlets and sales_by_outlet:
            health = self.health_calculator.calculate_health_score(
                outlet.outlet_id,
                sales,
                all_outlets,
                sales_by_outlet
            )
        else:
            # Create minimal health score
            health = HealthScore(
                outlet_id=outlet.outlet_id,
                score=50,
                category="STABLE",
                explanation="Basic health score with limited peer data"
            )
        
        # Detect anomalies
        anomalies = TrendAnalyzer.detect_anomalies(sales)
        
        return OutletPerformance(
            outlet_id=outlet.outlet_id,
            outlet_name=outlet.outlet_name,
            period="last_90_days",
            total_revenue=total_revenue,
            average_revenue=avg_revenue,
            transaction_count=transactions,
            average_order_value=aov,
            revenue_growth=growth,
            trend=trend,
            health_score=health,
            anomalies=anomalies[:3] if anomalies else []  # Top 3 anomalies
        )
    
    def _find_underperformance_reasons(self, 
                                       outlet: Outlet, 
                                       sales: List[SalesRecord],
                                       health: HealthScore) -> List[str]:
        """Find reasons for underperformance"""
        reasons = []
        
        if not sales:
            return ["No sales data available"]
        
        # Check revenue decline
        growth = RevenueAnalyzer.revenue_growth(sales)
        if growth is not None and growth < -10:
            reasons.append(f"Revenue declined by {abs(growth):.1f}%")
        
        # Check transaction decline
        transactions = SalesAnalyzer.transaction_count(sales)
        # Simplified: check if transactions are low (less than 30 days * avg)
        if transactions and len(sales) > 0:
            avg_transactions = transactions / len(sales)
            if avg_transactions < 30:
                reasons.append("Low transaction volume")
        
        # Check trend
        trend = TrendAnalyzer.detect_trend(sales)
        if trend == "decreasing":
            reasons.append("Consistent downward trend")
        
        # Check consecutive declines
        declines = TrendAnalyzer.consecutive_declines(sales)
        if declines >= 3:
            reasons.append(f"{declines} consecutive days of decline")
        
        # Check health score
        if health.score < 40:
            reasons.append(f"Low health score: {health.score:.1f}/100")
        
        # Check average order value
        aov = SalesAnalyzer.average_order_value(sales)
        if aov and aov < 500:
            reasons.append(f"Low average order value: ₹{aov:.2f}")
        
        if not reasons:
            reasons.append("Multiple metrics indicate underperformance")
        
        return reasons[:3]  # Limit to top 3 reasons
    
    def _generate_outlet_recommendations(self, 
                                         outlet: Outlet, 
                                         sales: List[SalesRecord],
                                         health: HealthScore) -> List[str]:
        """Generate recommendations for an outlet"""
        recommendations = []
        
        if not sales:
            return ["Collect sales data to assess performance"]
        
        trend = TrendAnalyzer.detect_trend(sales)
        
        if trend == "decreasing":
            recommendations.append("Investigate causes of revenue decline")
            recommendations.append("Review marketing and promotional activities")
            recommendations.append("Consider customer feedback analysis")
        elif trend == "increasing":
            recommendations.append("Maintain current strategies")
            recommendations.append("Identify and replicate success factors")
        else:
            recommendations.append("Monitor performance closely for changes")
            recommendations.append("Consider targeted improvements")
        
        if health.score < 50:
            recommendations.append("Conduct a detailed operational review")
            recommendations.append("Benchmark against top-performing outlets")
        
        # Check for anomalies
        anomalies = TrendAnalyzer.detect_anomalies(sales)
        if anomalies:
            recommendations.append("Investigate anomalous days for operational issues")
        
        # Check for specific issues
        aov = SalesAnalyzer.average_order_value(sales)
        if aov and aov < 500:
            recommendations.append("Review pricing and upselling strategies")
        
        if not recommendations:
            recommendations.append("Continue monitoring performance")
        
        return recommendations[:3]  # Limit to top 3
    
    def _generate_underperformer_recommendations(self, 
                                                 underperformers: List[UnderperformingOutlet]) -> List[str]:
        """Generate recommendations for underperformers"""
        recommendations = []
        
        for u in underperformers:
            rec = f"For {u.outlet_name}: "
            if u.reasons:
                if "revenue declined" in u.reasons[0]:
                    rec += "Consider promotional campaigns to boost revenue. "
                if "downward trend" in u.reasons[-1] if len(u.reasons) > 1 else "":
                    rec += "Review operational efficiency and customer experience. "
                if "low health score" in u.reasons[-1]:
                    rec += "Conduct comprehensive performance review. "
            if not rec.endswith(": "):
                recommendations.append(rec.strip())
        
        if not recommendations:
            recommendations.append("Conduct detailed performance review for all underperforming outlets.")
        
        return recommendations
    
    def _generate_basic_insights(self, performances: List[OutletPerformance]) -> List[str]:
        """Generate basic insights without LLM"""
        insights = []
        
        if not performances:
            return ["No performance data available"]
        
        # Filter performances with data
        valid_performances = [p for p in performances if p.total_revenue is not None and p.total_revenue > 0]
        
        if not valid_performances:
            return ["Insufficient data for insights"]
        
        # Find best and worst
        best = max(valid_performances, key=lambda p: p.total_revenue if p.total_revenue else 0)
        worst = min(valid_performances, key=lambda p: p.total_revenue if p.total_revenue else float('inf'))
        
        insights.append(f"Best performing outlet: {best.outlet_name} with revenue {best.total_revenue:.2f}")
        insights.append(f"Worst performing outlet: {worst.outlet_name} with revenue {worst.total_revenue:.2f}")
        
        # Count trends
        increasing = [p for p in valid_performances if p.trend == "increasing"]
        decreasing = [p for p in valid_performances if p.trend == "decreasing"]
        stable = [p for p in valid_performances if p.trend == "stable"]
        
        if increasing:
            insights.append(f"{len(increasing)} outlet(s) showing growth")
        if decreasing:
            insights.append(f"{len(decreasing)} outlet(s) showing decline")
        if stable:
            insights.append(f"{len(stable)} outlet(s) showing stable performance")
        
        # Average performance
        avg_revenue = sum(p.total_revenue for p in valid_performances) / len(valid_performances)
        insights.append(f"Average revenue across outlets: {avg_revenue:.2f}")
        
        return insights
    
    def _generate_basic_recommendations(self, performances: List[OutletPerformance]) -> List[str]:
        """Generate basic recommendations without LLM"""
        recommendations = []
        
        if not performances:
            return ["No performance data available"]
        
        # Find underperformers
        underperformers = [p for p in performances if p.health_score and p.health_score.category in ["UNDERPERFORMING", "AT_RISK"]]
        
        if underperformers:
            outlets = ", ".join([p.outlet_name for p in underperformers[:3]])
            if len(underperformers) > 3:
                outlets += f" and {len(underperformers)-3} more"
            recommendations.append(f"Prioritize improvement plans for: {outlets}")
        else:
            recommendations.append("Continue current strategies across all outlets")
        
        # Check declining trends
        decliners = [p for p in performances if p.trend == "decreasing"]
        if decliners:
            outlets = ", ".join([p.outlet_name for p in decliners[:3]])
            if len(decliners) > 3:
                outlets += f" and {len(decliners)-3} more"
            recommendations.append(f"Investigate declining performance at: {outlets}")
        
        # Check for outlets needing attention
        critical = [p for p in performances if p.health_score and p.health_score.category == "CRITICAL"]
        if critical:
            outlets = ", ".join([p.outlet_name for p in critical])
            recommendations.append(f"URGENT: Immediate action required for: {outlets}")
        
        if not recommendations:
            recommendations.append("Monitor performance and address any emerging issues")
        
        return recommendations[:3]
    
    def _extract_outlet_ids(self, query: str) -> List[str]:
        """Extract outlet IDs from a query"""
        # Look for patterns like OUT-101, OUT-102, etc.
        pattern = r'OUT-\d{3}'
        matches = re.findall(pattern, query.upper())
        return matches
    
    def _extract_time_period(self, query: str) -> str:
        """Extract time period from query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["today", "day"]):
            return "day"
        elif any(word in query_lower for word in ["week", "weekly"]):
            return "week"
        elif any(word in query_lower for word in ["month", "monthly"]):
            return "month"
        elif any(word in query_lower for word in ["quarter", "quarterly"]):
            return "quarter"
        else:
            return "default"


def create_agent(data_provider: Optional[DataProvider] = None, 
                 llm_provider: str = "mock") -> OutletPerformanceAgent:
    """Factory function to create an agent"""
    return OutletPerformanceAgent(
        data_provider=data_provider,
        llm_provider=llm_provider
    )