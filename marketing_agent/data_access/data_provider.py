import pandas as pd
import json
import os
from datetime import datetime, timedelta
import random
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from decimal import Decimal

logger = logging.getLogger(__name__)

@dataclass
class Campaign:
    campaign_id: str
    campaign_name: str
    campaign_type: str
    start_date: str
    end_date: str
    target_outlet: str
    target_region: str
    target_customer_segment: str
    campaign_status: str
    budget: float
    
@dataclass
class CampaignPerformance:
    campaign_id: str
    date: str
    impressions: int
    reach: int
    clicks: int
    conversions: int
    leads: int
    purchases: int
    revenue_generated: float
    campaign_cost: float
    likes: int
    shares: int
    comments: int
    views: int
    interactions: int

@dataclass
class Promotion:
    promotion_id: str
    campaign_id: str
    discount_percentage: float
    promotion_type: str
    redemptions: int
    revenue: float
    
class MarketingDataProvider:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self._ensure_sample_data()
        
    def _ensure_sample_data(self):
        """Create sample data if not exists"""
        campaigns_file = os.path.join(self.data_dir, "campaigns.csv")
        if not os.path.exists(campaigns_file):
            self._create_sample_campaigns()
            
        performance_file = os.path.join(self.data_dir, "campaign_performance.csv")
        if not os.path.exists(performance_file):
            self._create_sample_performance()
            
        promotions_file = os.path.join(self.data_dir, "promotions.csv")
        if not os.path.exists(promotions_file):
            self._create_sample_promotions()
            
    def _create_sample_campaigns(self):
        """Create sample campaign data"""
        campaigns = [
            Campaign(
                campaign_id="CAMP-001",
                campaign_name="Summer Sale 2026",
                campaign_type="Seasonal",
                start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                end_date=(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                target_outlet="All",
                target_region="North",
                target_customer_segment="All",
                campaign_status="Completed",
                budget=50000.0
            ),
            Campaign(
                campaign_id="CAMP-002",
                campaign_name="Weekend Flash Sale",
                campaign_type="Flash Sale",
                start_date=(datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
                end_date=(datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
                target_outlet="Outlet-101",
                target_region="North",
                target_customer_segment="Premium",
                campaign_status="Completed",
                budget=25000.0
            ),
            Campaign(
                campaign_id="CAMP-003",
                campaign_name="New Customer Acquisition",
                campaign_type="Acquisition",
                start_date=(datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
                end_date=(datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
                target_outlet="All",
                target_region="South",
                target_customer_segment="New",
                campaign_status="Active",
                budget=75000.0
            ),
            Campaign(
                campaign_id="CAMP-004",
                campaign_name="Holiday Special",
                campaign_type="Holiday",
                start_date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                end_date=(datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d"),
                target_outlet="Outlet-102",
                target_region="East",
                target_customer_segment="All",
                campaign_status="Active",
                budget=100000.0
            ),
            Campaign(
                campaign_id="CAMP-005",
                campaign_name="Social Media Blitz",
                campaign_type="Social Media",
                start_date=(datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"),
                end_date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                target_outlet="All",
                target_region="West",
                target_customer_segment="Young",
                campaign_status="Completed",
                budget=30000.0
            ),
        ]
        
        df = pd.DataFrame([asdict(c) for c in campaigns])
        df.to_csv(os.path.join(self.data_dir, "campaigns.csv"), index=False)
        logger.info(f"Created sample campaigns data with {len(campaigns)} campaigns")
        
    def _create_sample_performance(self):
        """Create sample performance data"""
        campaigns = self.get_campaigns()
        performance_data = []
        
        for campaign in campaigns:
            # Generate daily performance data
            days = 30
            for i in range(days):
                date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
                impressions = random.randint(5000, 50000)
                reach = int(impressions * random.uniform(0.7, 0.9))
                clicks = int(impressions * random.uniform(0.02, 0.08))
                conversions = int(clicks * random.uniform(0.05, 0.15))
                purchases = int(conversions * random.uniform(0.6, 0.9))
                revenue_generated = purchases * random.uniform(500, 2000)
                # Fix: Access budget as dictionary key
                campaign_budget = campaign.get('budget', 10000)
                campaign_cost = random.uniform(1000, min(5000, campaign_budget * 0.5))
                likes = int(impressions * random.uniform(0.01, 0.05))
                shares = int(likes * random.uniform(0.1, 0.3))
                comments = int(likes * random.uniform(0.2, 0.4))
                views = impressions * 2
                interactions = likes + shares + comments
                
                performance_data.append({
                    "campaign_id": campaign['campaign_id'],
                    "date": date,
                    "impressions": impressions,
                    "reach": reach,
                    "clicks": clicks,
                    "conversions": conversions,
                    "leads": conversions,
                    "purchases": purchases,
                    "revenue_generated": revenue_generated,
                    "campaign_cost": campaign_cost,
                    "likes": likes,
                    "shares": shares,
                    "comments": comments,
                    "views": views,
                    "interactions": interactions
                })
        
        df = pd.DataFrame(performance_data)
        df.to_csv(os.path.join(self.data_dir, "campaign_performance.csv"), index=False)
        logger.info(f"Created sample performance data with {len(performance_data)} records")
        
    def _create_sample_promotions(self):
        """Create sample promotion data"""
        campaigns = self.get_campaigns()
        promotions = []
        
        for i, campaign in enumerate(campaigns[:3]):  # Only first 3 campaigns have promotions
            for j in range(2):
                promotions.append(Promotion(
                    promotion_id=f"PROM-{i+1}{j+1}",
                    campaign_id=campaign['campaign_id'],
                    discount_percentage=float(random.choice([10, 15, 20, 25, 30])),
                    promotion_type=random.choice(["Discount", "BOGO", "Free Shipping"]),
                    redemptions=random.randint(50, 500),
                    revenue=random.uniform(10000, 50000)
                ))
        
        df = pd.DataFrame([asdict(p) for p in promotions])
        df.to_csv(os.path.join(self.data_dir, "promotions.csv"), index=False)
        logger.info(f"Created sample promotions data with {len(promotions)} promotions")
        
    def get_campaigns(self) -> List[Dict[str, Any]]:
        """Get all campaigns"""
        file_path = os.path.join(self.data_dir, "campaigns.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            return df.to_dict('records')
        return []
        
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign by ID"""
        campaigns = self.get_campaigns()
        for campaign in campaigns:
            if campaign['campaign_id'] == campaign_id:
                return campaign
        return None
        
    def get_campaign_performance(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get campaign performance data"""
        file_path = os.path.join(self.data_dir, "campaign_performance.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if campaign_id:
                df = df[df['campaign_id'] == campaign_id]
            return df.to_dict('records')
        return []
        
    def get_promotion_data(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get promotion data"""
        file_path = os.path.join(self.data_dir, "promotions.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if campaign_id:
                df = df[df['campaign_id'] == campaign_id]
            return df.to_dict('records')
        return []
        
    def get_engagement_data(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get engagement data"""
        performance = self.get_campaign_performance(campaign_id)
        return performance
        
    def get_conversion_data(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get conversion data"""
        performance = self.get_campaign_performance(campaign_id)
        return performance
        
    def get_campaign_costs(self, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get campaign costs"""
        performance = self.get_campaign_performance(campaign_id)
        return performance
        
    def get_historical_campaign_data(self) -> List[Dict[str, Any]]:
        """Get historical campaign data"""
        return self.get_campaigns()