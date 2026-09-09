import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from marketing_agent.agents.marketing_agent import MarketingAgent
from marketing_agent.data_access.data_provider import MarketingDataProvider

class TestMarketingAgent:
    def setup_method(self):
        """Setup test environment"""
        self.agent = MarketingAgent()
        
    def test_campaign_performance(self):
        """Test campaign performance analysis"""
        result = self.agent.process_query("How are our campaigns performing?")
        assert result['status'] == 'success'
        assert 'campaign_performance' in result['intent']
        assert 'insights' in result
        
    def test_roi_calculation(self):
        """Test ROI calculation"""
        result = self.agent.process_query("Calculate ROI for all campaigns")
        assert result['status'] == 'success'
        assert 'roi_analysis' in result['intent']
        assert 'insights' in result
        
    def test_campaign_comparison(self):
        """Test campaign comparison"""
        result = self.agent.process_query("Which campaign performed best?")
        assert result['status'] == 'success'
        assert 'campaign_comparison' in result['intent']
        
    def test_engagement_analysis(self):
        """Test engagement analysis"""
        result = self.agent.process_query("What is the customer engagement?")
        assert result['status'] == 'success'
        assert 'engagement_analysis' in result['intent']
        
    def test_underperforming_detection(self):
        """Test underperforming campaign detection"""
        result = self.agent.process_query("Which campaigns are underperforming?")
        assert result['status'] == 'success'
        assert 'underperforming' in result['intent']
        
    def test_successful_detection(self):
        """Test successful campaign detection"""
        result = self.agent.process_query("Which campaigns are successful?")
        assert result['status'] == 'success'
        assert 'successful' in result['intent']
        
    def test_trend_analysis(self):
        """Test trend analysis"""
        result = self.agent.process_query("What are the trends in campaign performance?")
        assert result['status'] == 'success'
        assert 'trends' in result['intent']
        
    def test_recommendations(self):
        """Test recommendation generation"""
        result = self.agent.process_query("Give me marketing recommendations")
        assert result['status'] == 'success'
        assert 'recommendations' in result['intent']
        
    def test_proposed_action_requires_approval(self):
        """Test proposed action requires approval"""
        result = self.agent.process_query("Increase Campaign CAMP-001 budget by ₹10,000")
        assert result['status'] == 'PENDING_APPROVAL'
        assert result['requires_human_approval'] == True
        assert 'proposed_action' in result['intent']
        
    def test_unauthorized_action_blocked(self):
        """Test unauthorized action is blocked"""
        result = self.agent.process_query("Launch a new 20% discount campaign")
        assert result['status'] == 'PENDING_APPROVAL'
        assert result['requires_human_approval'] == True
        
    def test_approval_workflow(self):
        """Test approval workflow"""
        # Create pending action
        result = self.agent.process_query("Increase Campaign CAMP-002 budget by ₹5,000")
        assert result['status'] == 'PENDING_APPROVAL'
        
        action_id = result['data']['id']
        
        # Approve it
        approval_result = self.agent.approve_action(action_id)
        assert approval_result['status'] == 'success'
        
    def test_rejection_workflow(self):
        """Test rejection workflow"""
        # Create pending action
        result = self.agent.process_query("Increase Campaign CAMP-003 budget by ₹5,000")
        assert result['status'] == 'PENDING_APPROVAL'
        
        action_id = result['data']['id']
        
        # Reject it
        rejection_result = self.agent.reject_action(action_id)
        assert rejection_result['status'] == 'success'
        
    def test_missing_data_handling(self):
        """Test handling of missing data"""
        # This should work even with minimal data
        result = self.agent.process_query("Show marketing ROI")
        assert result['status'] in ['success', 'error']
        
    def test_invalid_campaign_id(self):
        """Test handling of invalid campaign ID"""
        # This should handle gracefully
        result = self.agent.process_query("Analyze campaign INVALID-ID")
        assert result['status'] in ['success', 'error']