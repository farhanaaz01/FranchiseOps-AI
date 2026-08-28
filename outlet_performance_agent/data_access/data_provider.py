"""
Data Access Layer - Provides clean abstraction for data sources
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
import pandas as pd
import csv
import json
import logging
from pathlib import Path

from ..models.data_models import Outlet, SalesRecord

logger = logging.getLogger(__name__)


class DataProvider(ABC):
    """Abstract interface for data access"""
    
    @abstractmethod
    def get_outlets(self) -> List[Outlet]:
        """Get all outlets"""
        pass
    
    @abstractmethod
    def get_outlet(self, outlet_id: str) -> Optional[Outlet]:
        """Get a specific outlet by ID"""
        pass
    
    @abstractmethod
    def get_sales_data(self, 
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       outlet_ids: Optional[List[str]] = None) -> List[SalesRecord]:
        """Get sales data with optional filters"""
        pass
    
    @abstractmethod
    def get_outlet_sales(self, 
                         outlet_id: str,
                         start_date: Optional[date] = None,
                         end_date: Optional[date] = None) -> List[SalesRecord]:
        """Get sales data for a specific outlet"""
        pass
    
    @abstractmethod
    def get_historical_performance(self, 
                                   outlet_id: str,
                                   days: int = 90) -> Dict[str, Any]:
        """Get historical performance summary for an outlet"""
        pass


class CSVDataProvider(DataProvider):
    """Sample CSV-based data provider for standalone development"""
    
    def __init__(self, 
                 outlets_csv: str = "data/outlets.csv",
                 sales_csv: str = "data/sales_data.csv"):
        self.outlets_csv = Path(outlets_csv)
        self.sales_csv = Path(sales_csv)
        self._outlets = None
        self._sales = None
        self._load_data()
    
    def _load_data(self):
        """Load data from CSV files or create sample data"""
        try:
            # Try to load from CSV
            if self.outlets_csv.exists():
                df_outlets = pd.read_csv(self.outlets_csv)
            else:
                logger.warning("Outlet CSV not found, creating sample data")
                df_outlets = self._create_sample_outlets()
                self._save_sample_outlets(df_outlets)
            
            if self.sales_csv.exists():
                df_sales = pd.read_csv(self.sales_csv)
                # Convert date column
                if 'date' in df_sales.columns:
                    df_sales['date'] = pd.to_datetime(df_sales['date']).dt.date
            else:
                logger.warning("Sales CSV not found, creating sample data")
                df_sales = self._create_sample_sales()
                self._save_sample_sales(df_sales)
            
            self._outlets = df_outlets
            self._sales = df_sales
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self._outlets = self._create_sample_outlets()
            self._sales = self._create_sample_sales()
    
    def _create_sample_outlets(self) -> pd.DataFrame:
        """Create sample outlet data"""
        return pd.DataFrame([
            {"outlet_id": "OUT-101", "outlet_name": "Mumbai Central", "location": "Mumbai", 
             "city": "Mumbai", "region": "West", "outlet_type": "Flagship", 
             "opening_date": "2020-01-15", "status": "active", "operating_hours": 12.0},
            {"outlet_id": "OUT-102", "outlet_name": "Delhi North", "location": "Delhi", 
             "city": "Delhi", "region": "North", "outlet_type": "Standard", 
             "opening_date": "2020-03-20", "status": "active", "operating_hours": 10.0},
            {"outlet_id": "OUT-103", "outlet_name": "Bangalore East", "location": "Bangalore", 
             "city": "Bangalore", "region": "South", "outlet_type": "Standard", 
             "opening_date": "2020-06-10", "status": "active", "operating_hours": 10.0},
            {"outlet_id": "OUT-104", "outlet_name": "Pune East", "location": "Pune", 
             "city": "Pune", "region": "West", "outlet_type": "Small", 
             "opening_date": "2021-01-05", "status": "active", "operating_hours": 8.0},
            {"outlet_id": "OUT-105", "outlet_name": "Chennai South", "location": "Chennai", 
             "city": "Chennai", "region": "South", "outlet_type": "Standard", 
             "opening_date": "2020-09-15", "status": "active", "operating_hours": 10.0},
            {"outlet_id": "OUT-106", "outlet_name": "Hyderabad Central", "location": "Hyderabad", 
             "city": "Hyderabad", "region": "South", "outlet_type": "Flagship", 
             "opening_date": "2021-05-20", "status": "active", "operating_hours": 12.0},
            {"outlet_id": "OUT-107", "outlet_name": "Kolkata East", "location": "Kolkata", 
             "city": "Kolkata", "region": "East", "outlet_type": "Standard", 
             "opening_date": "2020-11-01", "status": "active", "operating_hours": 10.0},
            {"outlet_id": "OUT-108", "outlet_name": "Ahmedabad West", "location": "Ahmedabad", 
             "city": "Ahmedabad", "region": "West", "outlet_type": "Small", 
             "opening_date": "2021-08-10", "status": "active", "operating_hours": 8.0},
        ])
    
    def _create_sample_sales(self) -> pd.DataFrame:
        """Create sample sales data with realistic patterns"""
        import numpy as np
        np.random.seed(42)
        
        outlets = self._create_sample_outlets()['outlet_id'].tolist()
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        sales_data = []
        current_date = start_date
        
        # Base revenues and growth patterns for each outlet
        outlet_base_revenue = {
            "OUT-101": 5000,  # High performer
            "OUT-102": 4200,
            "OUT-103": 3800,
            "OUT-104": 2500,  # Underperformer
            "OUT-105": 4000,
            "OUT-106": 4800,
            "OUT-107": 3500,
            "OUT-108": 2800,
        }
        
        # Growth patterns (daily change)
        outlet_growth = {
            "OUT-101": 0.001,   # Steady growth
            "OUT-102": -0.0005,  # Slight decline
            "OUT-103": 0.0008,
            "OUT-104": -0.003,   # Declining
            "OUT-105": 0.0012,
            "OUT-106": 0.002,
            "OUT-107": 0.0003,
            "OUT-108": 0.0005,
        }
        
        # Weekly seasonality (day of week effect)
        weekly_pattern = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.1]  # Mon-Sun
        
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            weekday_factor = weekly_pattern[day_of_week]
            
            for outlet_id in outlets:
                base = outlet_base_revenue.get(outlet_id, 3000)
                growth = outlet_growth.get(outlet_id, 0)
                days_since_start = (current_date - start_date).days
                
                # Add growth, seasonality, and some randomness
                revenue = base * (1 + growth * days_since_start) * weekday_factor
                revenue *= (1 + np.random.normal(0, 0.05))  # Random noise
                revenue = max(revenue, 100)  # Minimum revenue
                
                # Calculate transactions (average order value around ₹500-₹800)
                aov = np.random.randint(400, 900)
                transactions = int(revenue / aov)
                
                sales_data.append({
                    "date": current_date,
                    "outlet_id": outlet_id,
                    "revenue": round(revenue, 2),
                    "transaction_count": transactions,
                    "sales_count": transactions,
                    "average_order_value": round(aov, 2),
                    "customer_count": int(transactions * np.random.uniform(0.7, 0.9))
                })
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(sales_data)
    
    def _save_sample_outlets(self, df: pd.DataFrame):
        """Save sample outlet data to CSV"""
        self.outlets_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.outlets_csv, index=False)
        logger.info(f"Saved sample outlet data to {self.outlets_csv}")
    
    def _save_sample_sales(self, df: pd.DataFrame):
        """Save sample sales data to CSV"""
        self.sales_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.sales_csv, index=False)
        logger.info(f"Saved sample sales data to {self.sales_csv}")
    
    def get_outlets(self) -> List[Outlet]:
        """Get all outlets from CSV"""
        outlets = []
        for _, row in self._outlets.iterrows():
            outlet = Outlet(
                outlet_id=row['outlet_id'],
                outlet_name=row['outlet_name'],
                location=row['location'],
                city=row.get('city'),
                region=row.get('region'),
                outlet_type=row.get('outlet_type'),
                opening_date=pd.to_datetime(row['opening_date']).date() if row.get('opening_date') else None,
                status=row.get('status', 'active'),
                operating_hours=row.get('operating_hours')
            )
            outlets.append(outlet)
        return outlets
    
    def get_outlet(self, outlet_id: str) -> Optional[Outlet]:
        """Get specific outlet by ID"""
        match = self._outlets[self._outlets['outlet_id'] == outlet_id]
        if match.empty:
            return None
        row = match.iloc[0]
        return Outlet(
            outlet_id=row['outlet_id'],
            outlet_name=row['outlet_name'],
            location=row['location'],
            city=row.get('city'),
            region=row.get('region'),
            outlet_type=row.get('outlet_type'),
            opening_date=pd.to_datetime(row['opening_date']).date() if row.get('opening_date') else None,
            status=row.get('status', 'active'),
            operating_hours=row.get('operating_hours')
        )
    
    def get_sales_data(self,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       outlet_ids: Optional[List[str]] = None) -> List[SalesRecord]:
        """Get sales data with filters"""
        df = self._sales.copy()
        
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
        if outlet_ids:
            df = df[df['outlet_id'].isin(outlet_ids)]
        
        records = []
        for _, row in df.iterrows():
            record = SalesRecord(
                date=row['date'],
                outlet_id=row['outlet_id'],
                revenue=row.get('revenue'),
                transaction_count=row.get('transaction_count'),
                sales_count=row.get('sales_count'),
                average_order_value=row.get('average_order_value'),
                customer_count=row.get('customer_count')
            )
            records.append(record)
        return records
    
    def get_outlet_sales(self,
                         outlet_id: str,
                         start_date: Optional[date] = None,
                         end_date: Optional[date] = None) -> List[SalesRecord]:
        """Get sales for specific outlet"""
        return self.get_sales_data(start_date, end_date, [outlet_id])
    
    def get_historical_performance(self,
                                   outlet_id: str,
                                   days: int = 90) -> Dict[str, Any]:
        """Get historical performance summary"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        sales = self.get_outlet_sales(outlet_id, start_date, end_date)
        
        if not sales:
            return {"error": "No sales data available"}
        
        revenues = [s.revenue for s in sales if s.revenue is not None]
        transactions = [s.transaction_count for s in sales if s.transaction_count is not None]
        
        if not revenues:
            return {"error": "No revenue data available"}
        
        return {
            "outlet_id": outlet_id,
            "period_days": days,
            "total_revenue": sum(revenues),
            "average_daily_revenue": sum(revenues) / len(revenues),
            "total_transactions": sum(transactions) if transactions else None,
            "days_with_data": len(sales),
            "start_date": start_date,
            "end_date": end_date
        }