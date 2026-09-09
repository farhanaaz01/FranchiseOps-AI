import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
import re

from ..data_access.data_provider import MarketingDataProvider
from ..utils.llm_interface import LLMInterface

logger = logging.getLogger(__name__)

class MarketingAgent:
    def __init__(self, data_provider: Optional[MarketingDataProvider] = None):
        self.data_provider = data_provider or MarketingDataProvider()
        self.llm = LLMInterface()
        self.approval_status = {
            'pending_actions': [],
            'approved_actions': [],
            'rejected_actions': []
        }
        
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query"""
        try:
            # Detect intent
            intent_result = self.llm.detect_intent(query)
            intent = intent_result.get('intent', 'general')
            
            # Execute appropriate function based on intent
            if intent == 'campaign_performance':
                return self.get_campaign_performance_analysis(query)
            elif intent == 'campaign_comparison':
                return self.compare_campaigns(query)
            elif intent == 'engagement_analysis':
                return self.analyze_engagement(query)
            elif intent == 'roi_analysis':
                return self.calculate_roi(query)
            elif intent == 'promotion_effectiveness':
                return self.analyze_promotions(query)
            elif intent == 'underperforming':
                return self.detect_underperforming_campaigns(query)
            elif intent == 'successful':
                return self.detect_successful_campaigns(query)
            elif intent == 'trends':
                return self.analyze_trends(query)
            elif intent == 'recommendations':
                return self.generate_recommendations(query)
            elif intent == 'proposed_action':
                return self.handle_proposed_action(query)
            else:
                return self.general_analysis(query)
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'intent': 'error',
                'status': 'error',
                'summary': f"An error occurred while processing your query: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
            
    def get_campaign_performance_analysis(self, query: str) -> Dict[str, Any]:
        """Get campaign performance analysis"""
        try:
            campaigns = self.data_provider.get_campaigns()
            performance = self.data_provider.get_campaign_performance()
            
            if not campaigns or not performance:
                return {
                    'intent': 'campaign_performance',
                    'status': 'error',
                    'summary': 'No campaign data available for performance analysis.',
                    'data': [],
                    'insights': ['No data available'],
                    'recommendations': [],
                    'requires_human_approval': False
                }
                
            # Calculate metrics for each campaign
            results = []
            for campaign in campaigns:
                camp_perf = [p for p in performance if p['campaign_id'] == campaign['campaign_id']]
                if camp_perf:
                    metrics = self._calculate_campaign_metrics(camp_perf)
                    results.append({
                        'campaign_id': campaign['campaign_id'],
                        'campaign_name': campaign['campaign_name'],
                        **metrics
                    })
                    
            # Generate insights
            insights = self._generate_performance_insights(results)
            recommendations = self._generate_recommendations_from_insights(insights)
            
            # Get LLM response
            llm_response = self.llm.generate_response({
                'intent': 'campaign_performance',
                'results': results[:5],  # Limit results for LLM
                'insights': insights[:5]
            }, query)
            
            return {
                'intent': 'campaign_performance',
                'status': 'success',
                'summary': llm_response.get('response', 'Performance analysis complete'),
                'data': results,
                'insights': insights,
                'recommendations': recommendations,
                'requires_human_approval': False,
                'llm_source': llm_response.get('source', 'fallback')
            }
        except Exception as e:
            logger.error(f"Error in campaign performance analysis: {e}")
            return {
                'intent': 'campaign_performance',
                'status': 'error',
                'summary': f"Error analyzing campaign performance: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
        
    def compare_campaigns(self, query: str) -> Dict[str, Any]:
        """Compare campaigns"""
        try:
            campaigns = self.data_provider.get_campaigns()
            performance = self.data_provider.get_campaign_performance()
            
            if not campaigns or not performance:
                return {
                    'intent': 'campaign_comparison',
                    'status': 'error',
                    'summary': 'No campaign data available for comparison.',
                    'data': [],
                    'insights': ['No data available'],
                    'recommendations': [],
                    'requires_human_approval': False
                }
                
            # Calculate metrics for all campaigns
            campaign_metrics = []
            for campaign in campaigns:
                camp_perf = [p for p in performance if p['campaign_id'] == campaign['campaign_id']]
                if camp_perf:
                    metrics = self._calculate_campaign_metrics(camp_perf)
                    campaign_metrics.append({
                        'campaign_id': campaign['campaign_id'],
                        'campaign_name': campaign['campaign_name'],
                        **metrics
                    })
                    
            if not campaign_metrics:
                return {
                    'intent': 'campaign_comparison',
                    'status': 'error',
                    'summary': 'No campaign metrics available for comparison.',
                    'data': [],
                    'insights': ['No valid metrics found'],
                    'recommendations': [],
                    'requires_human_approval': False
                }
                
            # Find best performers
            valid_roi = [c for c in campaign_metrics if c.get('roi') is not None]
            best_roi = max(valid_roi, key=lambda x: x.get('roi', 0)) if valid_roi else None
            best_conversion = max(campaign_metrics, key=lambda x: x.get('conversion_rate', 0)) if campaign_metrics else None
            best_engagement = max(campaign_metrics, key=lambda x: x.get('engagement_rate', 0)) if campaign_metrics else None
            
            insights = []
            if best_roi:
                insights.append(f"Best ROI Campaign: {best_roi['campaign_name']} with {best_roi['roi']:.1f}% ROI")
            if best_conversion:
                insights.append(f"Best Conversion Campaign: {best_conversion['campaign_name']} with {best_conversion['conversion_rate']:.1f}% conversion")
            if best_engagement:
                insights.append(f"Best Engagement Campaign: {best_engagement['campaign_name']} with {best_engagement['engagement_rate']:.1f}% engagement")
                
            llm_response = self.llm.generate_response({
                'intent': 'campaign_comparison',
                'results': campaign_metrics[:5],
                'insights': insights[:3]
            }, query)
            
            return {
                'intent': 'campaign_comparison',
                'status': 'success',
                'summary': llm_response.get('response', 'Campaign comparison complete'),
                'data': campaign_metrics,
                'insights': insights,
                'recommendations': [],
                'requires_human_approval': False,
                'llm_source': llm_response.get('source', 'fallback')
            }
        except Exception as e:
            logger.error(f"Error in campaign comparison: {e}")
            return {
                'intent': 'campaign_comparison',
                'status': 'error',
                'summary': f"Error comparing campaigns: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
        
    def analyze_engagement(self, query: str) -> Dict[str, Any]:
        """Analyze customer engagement"""
        try:
            engagement_data = self.data_provider.get_engagement_data()
            
            if not engagement_data:
                return {
                    'intent': 'engagement_analysis',
                    'status': 'error',
                    'summary': 'No engagement data available.',
                    'data': [],
                    'insights': ['No engagement data found'],
                    'recommendations': [],
                    'requires_human_approval': False
                }
                
            # Calculate engagement metrics
            df = pd.DataFrame(engagement_data)
            total_engagement = df['interactions'].sum()
            total_reach = df['reach'].sum()
            engagement_rate = (total_engagement / total_reach * 100) if total_reach > 0 else 0
            
            # Detect engagement trends
            trend = self._detect_trend(df, 'interactions')
            
            insights = [
                f"Total engagements: {total_engagement:,}",
                f"Overall engagement rate: {engagement_rate:.2f}%",
                f"Engagement trend: {trend}"
            ]
            
            recommendations = []
            if engagement_rate < 2:
                recommendations.append("Consider improving content quality and targeting")
            if trend == 'Declining':
                recommendations.append("Review recent campaigns and adjust strategy")
                
            llm_response = self.llm.generate_response({
                'intent': 'engagement_analysis',
                'total_engagement': total_engagement,
                'engagement_rate': engagement_rate,
                'trend': trend
            }, query)
            
            return {
                'intent': 'engagement_analysis',
                'status': 'success',
                'summary': llm_response.get('response', 'Engagement analysis complete'),
                'data': engagement_data[:100],  # Limit data
                'insights': insights,
                'recommendations': recommendations,
                'requires_human_approval': False,
                'llm_source': llm_response.get('source', 'fallback')
            }
        except Exception as e:
            logger.error(f"Error in engagement analysis: {e}")
            return {
                'intent': 'engagement_analysis',
                'status': 'error',
                'summary': f"Error analyzing engagement: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
        
    def calculate_roi(self, query: str) -> Dict[str, Any]:
        """Calculate ROI for campaigns"""
        try:
            campaigns = self.data_provider.get_campaigns()
            performance = self.data_provider.get_campaign_performance()
            
            roi_results = []
            for campaign in campaigns:
                camp_perf = [p for p in performance if p['campaign_id'] == campaign['campaign_id']]
                if camp_perf:
                    total_cost = sum(p['campaign_cost'] for p in camp_perf)
                    total_revenue = sum(p['revenue_generated'] for p in camp_perf)
                    
                    if total_cost > 0:
                        roi = ((total_revenue - total_cost) / total_cost) * 100
                    else:
                        roi = None
                        
                    roi_results.append({
                        'campaign_id': campaign['campaign_id'],
                        'campaign_name': campaign['campaign_name'],
                        'total_cost': total_cost,
                        'total_revenue': total_revenue,
                        'roi': roi,
                        'roi_calculable': roi is not None
                    })
                    
            insights = []
            if roi_results:
                valid_roi = [r for r in roi_results if r['roi'] is not None]
                if valid_roi:
                    best_roi = max(valid_roi, key=lambda x: x['roi'])
                    avg_roi = np.mean([r['roi'] for r in valid_roi])
                    insights.append(f"Best ROI: {best_roi['campaign_name']} with {best_roi['roi']:.1f}% ROI")
                    insights.append(f"Average ROI across campaigns: {avg_roi:.1f}%")
                else:
                    insights.append("ROI cannot be calculated for any campaign due to missing cost data.")
                    
            llm_response = self.llm.generate_response({
                'intent': 'roi_analysis',
                'results': roi_results[:5],
                'insights': insights[:3]
            }, query)
            
            return {
                'intent': 'roi_analysis',
                'status': 'success',
                'summary': llm_response.get('response', 'ROI analysis complete'),
                'data': roi_results,
                'insights': insights,
                'recommendations': [],
                'requires_human_approval': False,
                'llm_source': llm_response.get('source', 'fallback')
            }
        except Exception as e:
            logger.error(f"Error in ROI calculation: {e}")
            return {
                'intent': 'roi_analysis',
                'status': 'error',
                'summary': f"Error calculating ROI: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
        
    def analyze_promotions(self, query: str) -> Dict[str, Any]:
        """Analyze promotion effectiveness"""
        try:
            promotions = self.data_provider.get_promotion_data()
            
            if not promotions:
                return {
                    'intent': 'promotion_effectiveness',
                    'status': 'error',
                    'summary': 'No promotion data available.',
                    'data': [],
                    'insights': ['No promotion data found'],
                    'recommendations': [],
                    'requires_human_approval': False
                }
                
            df = pd.DataFrame(promotions)
            total_redemptions = df['redemptions'].sum()
            total_revenue = df['revenue'].sum()
            avg_discount = df['discount_percentage'].mean()
            
            insights = [
                f"Total promotions redeemed: {total_redemptions:,}",
                f"Total revenue from promotions: ₹{total_revenue:,.2f}",
                f"Average discount: {avg_discount:.1f}%"
            ]
            
            recommendations = []
            if avg_discount > 25:
                recommendations.append("Consider reducing discount percentages to improve profitability")
            if total_redemptions < 100:
                recommendations.append("Improve promotion visibility and awareness")
                
            llm_response = self.llm.generate_response({
                'intent': 'promotion_effectiveness',
                'total_redemptions': total_redemptions,
                'total_revenue': total_revenue,
                'avg_discount': avg_discount
            }, query)
            
            return {
                'intent': 'promotion_effectiveness',
                'status': 'success',
                'summary': llm_response.get('response', 'Promotion analysis complete'),
                'data': promotions,
                'insights': insights,
                'recommendations': recommendations,
                'requires_human_approval': False,
                'llm_source': llm_response.get('source', 'fallback')
            }
        except Exception as e:
            logger.error(f"Error in promotion analysis: {e}")
            return {
                'intent': 'promotion_effectiveness',
                'status': 'error',
                'summary': f"Error analyzing promotions: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
        
    def detect_underperforming_campaigns(self, query: str) -> Dict[str, Any]:
        """Detect underperforming campaigns"""
        try:
            campaigns = self.data_provider.get_campaigns()
            performance = self.data_provider.get_campaign_performance()
            
            if not campaigns or not performance:
                return {
                    'intent': 'underperforming',
                    'status': 'error',
                    'summary': 'No campaign data available.',
                    'data': [],
                    'insights': ['No data available'],
                    'recommendations': [],
                    'requires_human_approval': False
                }
                
            underperforming = []
            for campaign in campaigns:
                camp_perf = [p for p in performance if p['campaign_id'] == campaign['campaign_id']]
                if camp_perf:
                    metrics = self._calculate_campaign_metrics(camp_perf)
                    conversion_rate = metrics.get('conversion_rate', 0)
                    engagement_rate = metrics.get('engagement_rate', 0)
                    
                    if conversion_rate < 2 or engagement_rate < 1:
                        reasons = []
                        if conversion_rate < 2:
                            reasons.append('Low conversion rate')
                        if engagement_rate < 1:
                            reasons.append('Low engagement')
                            
                        underperforming.append({
                            'campaign_id': campaign['campaign_id'],
                            'campaign_name': campaign['campaign_name'],
                            'metrics': metrics,
                            'reasons': reasons
                        })
                        
            insights = []
            if underperforming:
                insights.append(f"Found {len(underperforming)} underperforming campaigns")
                for u in underperforming[:5]:  # Limit display
                    insights.append(f"- {u['campaign_name']}: {', '.join(u['reasons'])}")
            else:
                insights.append("No underperforming campaigns detected")
                
            recommendations = []
            for u in underperforming:
                for reason in u['reasons']:
                    if 'conversion' in reason.lower():
                        recommendations.append(f"Review landing page and offer for {u['campaign_name']}")
                    if 'engagement' in reason.lower():
                        recommendations.append(f"Improve content quality for {u['campaign_name']}")
                        
            llm_response = self.llm.generate_response({
                'intent': 'underperforming',
                'results': underperforming[:5],
                'insights': insights[:3]
            }, query)
            
            return {
                'intent': 'underperforming',
                'status': 'success',
                'summary': llm_response.get('response', 'Underperforming campaign analysis complete'),
                'data': underperforming,
                'insights': insights,
                'recommendations': recommendations,
                'requires_human_approval': False,
                'llm_source': llm_response.get('source', 'fallback')
            }
        except Exception as e:
            logger.error(f"Error in underperforming detection: {e}")
            return {
                'intent': 'underperforming',
                'status': 'error',
                'summary': f"Error detecting underperforming campaigns: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
        
    def detect_successful_campaigns(self, query: str) -> Dict[str, Any]:
        """Detect successful campaigns"""
        try:
            campaigns = self.data_provider.get_campaigns()
            performance = self.data_provider.get_campaign_performance()
            
            if not campaigns or not performance:
                return {
                    'intent': 'successful',
                    'status': 'error',
                    'summary': 'No campaign data available.',
                    'data': [],
                    'insights': ['No data available'],
                    'recommendations': [],
                    'requires_human_approval': False
                }
                
            successful = []
            for campaign in campaigns:
                camp_perf = [p for p in performance if p['campaign_id'] == campaign['campaign_id']]
                if camp_perf:
                    metrics = self._calculate_campaign_metrics(camp_perf)
                    conversion_rate = metrics.get('conversion_rate', 0)
                    engagement_rate = metrics.get('engagement_rate', 0)
                    roi = metrics.get('roi', -100)
                    
                    if conversion_rate > 10 and engagement_rate > 5 and roi is not None and roi > 50:
                        successful.append({
                            'campaign_id': campaign['campaign_id'],
                            'campaign_name': campaign['campaign_name'],
                            'metrics': metrics,
                            'reasons': [
                                f"High conversion rate: {conversion_rate:.1f}%",
                                f"Strong engagement rate: {engagement_rate:.1f}%",
                                f"Good ROI: {roi:.1f}%"
                            ]
                        })
                        
            insights = []
            if successful:
                insights.append(f"Found {len(successful)} successful campaigns")
                for s in successful[:5]:
                    insights.append(f"- {s['campaign_name']}: {', '.join(s['reasons'])}")
            else:
                insights.append("No campaigns meeting all success criteria found")
                
            recommendations = []
            for s in successful[:3]:
                recommendations.append(f"Consider replicating strategies from {s['campaign_name']} in other campaigns")
                
            llm_response = self.llm.generate_response({
                'intent': 'successful',
                'results': successful[:5],
                'insights': insights[:3]
            }, query)
            
            return {
                'intent': 'successful',
                'status': 'success',
                'summary': llm_response.get('response', 'Successful campaign analysis complete'),
                'data': successful,
                'insights': insights,
                'recommendations': recommendations,
                'requires_human_approval': False,
                'llm_source': llm_response.get('source', 'fallback')
            }
        except Exception as e:
            logger.error(f"Error in successful campaign detection: {e}")
            return {
                'intent': 'successful',
                'status': 'error',
                'summary': f"Error detecting successful campaigns: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
        
    def analyze_trends(self, query: str) -> Dict[str, Any]:
        """Analyze campaign trends"""
        try:
            performance = self.data_provider.get_campaign_performance()
            
            if not performance:
                return {
                    'intent': 'trends',
                    'status': 'error',
                    'summary': 'No performance data available for trend analysis.',
                    'data': [],
                    'insights': ['No data available'],
                    'recommendations': [],
                    'requires_human_approval': False
                }
                
            df = pd.DataFrame(performance)
            df['date'] = pd.to_datetime(df['date'])
            
            # Calculate daily trends
            daily_trends = df.groupby('date').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'conversions': 'sum',
                'revenue_generated': 'sum'
            }).reset_index()
            
            # Detect trends
            if len(daily_trends) >= 3:
                conversion_trend = self._detect_trend(daily_trends, 'conversions')
                revenue_trend = self._detect_trend(daily_trends, 'revenue_generated')
                impressions_trend = self._detect_trend(daily_trends, 'impressions')
            else:
                conversion_trend = 'Insufficient data'
                revenue_trend = 'Insufficient data'
                impressions_trend = 'Insufficient data'
                
            insights = [
                f"Conversion trend: {conversion_trend}",
                f"Revenue trend: {revenue_trend}",
                f"Impressions trend: {impressions_trend}"
            ]
            
            recommendations = []
            if conversion_trend == 'Declining':
                recommendations.append("Investigate and address factors causing declining conversions")
            if revenue_trend == 'Declining':
                recommendations.append("Review pricing and promotional strategies")
            if impressions_trend == 'Declining':
                recommendations.append("Review advertising spend and channel effectiveness")
                
            llm_response = self.llm.generate_response({
                'intent': 'trends',
                'conversion_trend': conversion_trend,
                'revenue_trend': revenue_trend,
                'insights': insights[:3]
            }, query)
            
            return {
                'intent': 'trends',
                'status': 'success',
                'summary': llm_response.get('response', 'Trend analysis complete'),
                'data': daily_trends.to_dict('records')[:30],  # Limit data
                'insights': insights,
                'recommendations': recommendations,
                'requires_human_approval': False,
                'llm_source': llm_response.get('source', 'fallback')
            }
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return {
                'intent': 'trends',
                'status': 'error',
                'summary': f"Error analyzing trends: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
        
    def generate_recommendations(self, query: str) -> Dict[str, Any]:
        """Generate marketing recommendations"""
        try:
            performance = self.data_provider.get_campaign_performance()
            
            if not performance:
                return {
                    'intent': 'recommendations',
                    'status': 'error',
                    'summary': 'No performance data available for recommendations.',
                    'data': [],
                    'insights': ['No data available'],
                    'recommendations': ['Gather campaign performance data first'],
                    'requires_human_approval': False
                }
                
            # Analyze performance to generate recommendations
            df = pd.DataFrame(performance)
            
            total_impressions = df['impressions'].sum()
            total_clicks = df['clicks'].sum()
            total_conversions = df['conversions'].sum()
            
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            
            recommendations = []
            insights = []
            
            if ctr < 2:
                recommendations.append("Improve click-through rates by optimizing ad creative and messaging")
                insights.append(f"Current CTR is {ctr:.2f}% - below industry average")
            elif ctr > 5:
                insights.append(f"Strong CTR at {ctr:.2f}% - ad creative is effective")
                
            if conversion_rate < 5:
                recommendations.append("Improve conversion rates by optimizing landing pages and offers")
                insights.append(f"Current conversion rate is {conversion_rate:.2f}% - below industry average")
            elif conversion_rate > 10:
                insights.append(f"Excellent conversion rate at {conversion_rate:.2f}% - landing pages are effective")
                
            # Check for campaigns with high potential
            campaigns = self.data_provider.get_campaigns()
            for campaign in campaigns:
                camp_perf = [p for p in performance if p['campaign_id'] == campaign['campaign_id']]
                if camp_perf:
                    metrics = self._calculate_campaign_metrics(camp_perf)
                    if metrics.get('conversion_rate', 0) > 10:
                        recommendations.append(f"Consider allocating more budget to {campaign['campaign_name']}")
                        
            if not recommendations:
                recommendations.append("Continue current strategy - campaigns are performing well")
                
            llm_response = self.llm.generate_response({
                'intent': 'recommendations',
                'ctr': ctr,
                'conversion_rate': conversion_rate,
                'recommendations': recommendations[:5]
            }, query)
            
            return {
                'intent': 'recommendations',
                'status': 'success',
                'summary': llm_response.get('response', 'Recommendations generated'),
                'data': [],
                'insights': insights,
                'recommendations': recommendations,
                'requires_human_approval': False,
                'llm_source': llm_response.get('source', 'fallback')
            }
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {
                'intent': 'recommendations',
                'status': 'error',
                'summary': f"Error generating recommendations: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
        
    def handle_proposed_action(self, query: str) -> Dict[str, Any]:
        """Handle proposed marketing actions that require approval"""
        try:
            # Extract action details from query
            action_details = self._extract_action_details(query)
            
            # Check if action requires approval (spending money or consequential)
            requires_approval = self._requires_approval(action_details)
            
            if requires_approval:
                # Create pending approval request
                approval_request = {
                    'id': f"ACTION-{len(self.approval_status['pending_actions']) + 1}",
                    'query': query,
                    'action_details': action_details,
                    'status': 'PENDING_APPROVAL',
                    'timestamp': datetime.now().isoformat()
                }
                self.approval_status['pending_actions'].append(approval_request)
                
                return {
                    'intent': 'proposed_action',
                    'status': 'PENDING_APPROVAL',
                    'summary': f"Proposed action requires Human Head approval: {action_details.get('description', 'Marketing action')}",
                    'data': approval_request,
                    'insights': ['This action requires Human Head approval before execution'],
                    'recommendations': [],
                    'requires_human_approval': True,
                    'proposed_action': action_details
                }
            else:
                return {
                    'intent': 'proposed_action',
                    'status': 'approved',
                    'summary': f"Action approved: {action_details.get('description', 'Marketing action')}",
                    'data': action_details,
                    'insights': [],
                    'recommendations': [],
                    'requires_human_approval': False
                }
        except Exception as e:
            logger.error(f"Error handling proposed action: {e}")
            return {
                'intent': 'proposed_action',
                'status': 'error',
                'summary': f"Error processing proposed action: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
            
    def approve_action(self, action_id: str) -> Dict[str, Any]:
        """Approve a pending action"""
        try:
            for i, action in enumerate(self.approval_status['pending_actions']):
                if action['id'] == action_id:
                    action['status'] = 'APPROVED'
                    self.approval_status['pending_actions'].pop(i)
                    self.approval_status['approved_actions'].append(action)
                    return {
                        'status': 'success',
                        'message': f"Action {action_id} approved",
                        'action': action
                    }
            return {
                'status': 'error',
                'message': f"Action {action_id} not found"
            }
        except Exception as e:
            logger.error(f"Error approving action: {e}")
            return {
                'status': 'error',
                'message': f"Error approving action: {str(e)}"
            }
            
    def reject_action(self, action_id: str) -> Dict[str, Any]:
        """Reject a pending action"""
        try:
            for i, action in enumerate(self.approval_status['pending_actions']):
                if action['id'] == action_id:
                    action['status'] = 'REJECTED'
                    self.approval_status['pending_actions'].pop(i)
                    self.approval_status['rejected_actions'].append(action)
                    return {
                        'status': 'success',
                        'message': f"Action {action_id} rejected",
                        'action': action
                    }
            return {
                'status': 'error',
                'message': f"Action {action_id} not found"
            }
        except Exception as e:
            logger.error(f"Error rejecting action: {e}")
            return {
                'status': 'error',
                'message': f"Error rejecting action: {str(e)}"
            }
        
    def general_analysis(self, query: str) -> Dict[str, Any]:
        """General marketing analysis"""
        try:
            campaigns = self.data_provider.get_campaigns()
            performance = self.data_provider.get_campaign_performance()
            
            if not campaigns or not performance:
                return {
                    'intent': 'general',
                    'status': 'error',
                    'summary': 'No data available for general analysis.',
                    'data': [],
                    'insights': ['No data available'],
                    'recommendations': [],
                    'requires_human_approval': False
                }
                
            total_campaigns = len(campaigns)
            active_campaigns = len([c for c in campaigns if c['campaign_status'] == 'Active'])
            total_spend = sum(p['campaign_cost'] for p in performance)
            total_revenue = sum(p['revenue_generated'] for p in performance)
            
            insights = [
                f"Total campaigns: {total_campaigns}",
                f"Active campaigns: {active_campaigns}",
                f"Total spend: ₹{total_spend:,.2f}",
                f"Total revenue: ₹{total_revenue:,.2f}"
            ]
            
            if total_spend > 0:
                overall_roi = ((total_revenue - total_spend) / total_spend) * 100
                insights.append(f"Overall ROI: {overall_roi:.1f}%")
                
            llm_response = self.llm.generate_response({
                'intent': 'general',
                'total_campaigns': total_campaigns,
                'active_campaigns': active_campaigns,
                'total_spend': total_spend,
                'total_revenue': total_revenue
            }, query)
            
            return {
                'intent': 'general',
                'status': 'success',
                'summary': llm_response.get('response', 'General analysis complete'),
                'data': {
                    'total_campaigns': total_campaigns,
                    'active_campaigns': active_campaigns,
                    'total_spend': total_spend,
                    'total_revenue': total_revenue
                },
                'insights': insights,
                'recommendations': [],
                'requires_human_approval': False,
                'llm_source': llm_response.get('source', 'fallback')
            }
        except Exception as e:
            logger.error(f"Error in general analysis: {e}")
            return {
                'intent': 'general',
                'status': 'error',
                'summary': f"Error in general analysis: {str(e)}",
                'data': [],
                'insights': [],
                'recommendations': [],
                'requires_human_approval': False
            }
        
    # Helper methods
    def _calculate_campaign_metrics(self, performance_data: List[Dict]) -> Dict[str, Any]:
        """Calculate campaign metrics"""
        try:
            df = pd.DataFrame(performance_data)
            
            total_impressions = df['impressions'].sum()
            total_clicks = df['clicks'].sum()
            total_conversions = df['conversions'].sum()
            total_revenue = df['revenue_generated'].sum()
            total_cost = df['campaign_cost'].sum()
            total_interactions = df['interactions'].sum()
            total_reach = df['reach'].sum()
            
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            engagement_rate = (total_interactions / total_reach * 100) if total_reach > 0 else 0
            roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else None
            
            return {
                'total_impressions': int(total_impressions),
                'total_clicks': int(total_clicks),
                'total_conversions': int(total_conversions),
                'total_revenue': float(total_revenue),
                'total_cost': float(total_cost),
                'ctr': float(ctr),
                'conversion_rate': float(conversion_rate),
                'engagement_rate': float(engagement_rate),
                'roi': float(roi) if roi is not None else None
            }
        except Exception as e:
            logger.error(f"Error calculating campaign metrics: {e}")
            return {
                'total_impressions': 0,
                'total_clicks': 0,
                'total_conversions': 0,
                'total_revenue': 0.0,
                'total_cost': 0.0,
                'ctr': 0.0,
                'conversion_rate': 0.0,
                'engagement_rate': 0.0,
                'roi': None
            }
        
    def _detect_trend(self, df: pd.DataFrame, column: str) -> str:
        """Detect trend in data"""
        try:
            if len(df) < 3:
                return 'Insufficient data'
                
            # Calculate moving average
            values = df[column].values
            mid_point = len(values) // 2
            first_half_avg = np.mean(values[:mid_point])
            second_half_avg = np.mean(values[mid_point:])
            
            if second_half_avg > first_half_avg * 1.1:
                return 'Increasing'
            elif second_half_avg < first_half_avg * 0.9:
                return 'Declining'
            else:
                return 'Stable'
        except Exception as e:
            logger.error(f"Error detecting trend: {e}")
            return 'Unable to determine'
            
    def _generate_performance_insights(self, results: List[Dict]) -> List[str]:
        """Generate insights from performance data"""
        insights = []
        
        if not results:
            return insights
            
        try:
            # Find best performers
            valid_roi = [r for r in results if r.get('roi') is not None]
            if valid_roi:
                best_roi = max(valid_roi, key=lambda x: x.get('roi', -100))
                insights.append(f"Top ROI campaign: {best_roi['campaign_name']} with {best_roi['roi']:.1f}% ROI")
                
            if results:
                best_conversion = max(results, key=lambda x: x.get('conversion_rate', 0))
                insights.append(f"Top conversion campaign: {best_conversion['campaign_name']} with {best_conversion['conversion_rate']:.1f}% conversion")
                
                best_engagement = max(results, key=lambda x: x.get('engagement_rate', 0))
                insights.append(f"Top engagement campaign: {best_engagement['campaign_name']} with {best_engagement['engagement_rate']:.1f}% engagement")
            
            # Check for campaigns needing attention
            for r in results:
                if r.get('conversion_rate', 100) < 2:
                    insights.append(f"Campaign {r['campaign_name']} has low conversion rate ({r['conversion_rate']:.1f}%)")
                if r.get('engagement_rate', 100) < 1:
                    insights.append(f"Campaign {r['campaign_name']} has low engagement rate ({r['engagement_rate']:.1f}%)")
                    
            return insights
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return ["Unable to generate insights"]
        
    def _generate_recommendations_from_insights(self, insights: List[str]) -> List[str]:
        """Generate recommendations from insights"""
        recommendations = []
        
        for insight in insights:
            try:
                if 'low conversion' in insight.lower():
                    recommendations.append("Review landing page experience and offer relevance")
                if 'low engagement' in insight.lower():
                    recommendations.append("Review content quality and audience targeting")
                if 'top roi' in insight.lower():
                    recommendations.append("Consider replicating this campaign strategy")
            except:
                continue
                
        return recommendations
        
    def _extract_action_details(self, query: str) -> Dict[str, Any]:
        """Extract action details from query"""
        action_details = {
            'description': query,
            'type': 'marketing_action',
            'requires_approval': True
        }
        
        try:
            # Check for budget increase requests
            if 'increase' in query.lower() and 'budget' in query.lower():
                # Try to extract amount
                amounts = re.findall(r'₹?(\d{1,3}(?:,\d{3})*|\d+)', query)
                if amounts:
                    action_details['amount'] = float(amounts[0].replace(',', ''))
                    action_details['type'] = 'budget_increase'
                    
            # Check for campaign launch requests
            if 'launch' in query.lower():
                action_details['type'] = 'campaign_launch'
                
            # Extract campaign ID if present
            campaign_match = re.search(r'CAMP-\d{3}', query)
            if campaign_match:
                action_details['campaign_id'] = campaign_match.group()
                
        except Exception as e:
            logger.error(f"Error extracting action details: {e}")
            
        return action_details
        
    def _requires_approval(self, action_details: Dict[str, Any]) -> bool:
        """Check if action requires human approval"""
        try:
            action_type = action_details.get('type', '')
            
            # Actions that always require approval
            if action_type in ['budget_increase', 'campaign_launch']:
                return True
                
            # Check for financial implications
            if 'amount' in action_details and action_details['amount'] > 0:
                return True
                
            # Default: require approval for any proposed action
            return True
        except:
            return True