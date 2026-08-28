"""
Stock analysis module for inventory analytics.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from enum import Enum
import statistics

from ..data_access.interfaces import StockLevel, DemandHistory, StockMovement


class StockStatus(Enum):
    """Stock status classifications."""
    HEALTHY = "HEALTHY"
    LOW_STOCK = "LOW_STOCK"
    CRITICAL_STOCK = "CRITICAL_STOCK"
    STOCKOUT = "STOCKOUT"
    OVERSTOCKED = "OVERSTOCKED"
    EXPIRING = "EXPIRING"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class StockAnalyzer:
    """
    Analyzes stock levels and movements.
    Provides methods for stock status, coverage, and movement analysis.
    """
    
    def __init__(self, low_stock_days: int = 3, 
                 critical_stock_days: int = 1,
                 overstock_days: int = 14):
        """
        Initialize the stock analyzer.
        
        Args:
            low_stock_days: Days of stock that triggers LOW_STOCK
            critical_stock_days: Days of stock that triggers CRITICAL_STOCK
            overstock_days: Days of stock that triggers OVERSTOCKED
        """
        self.low_stock_days = low_stock_days
        self.critical_stock_days = critical_stock_days
        self.overstock_days = overstock_days
    
    def calculate_average_daily_demand(self, demand_history: List[DemandHistory],
                                      days: Optional[int] = None) -> float:
        """
        Calculate average daily demand from demand history.
        
        Args:
            demand_history: List of demand history entries
            days: Number of recent days to consider (None = all)
        
        Returns:
            Average daily demand
        """
        if not demand_history:
            return 0.0
        
        # Sort by date and get recent data
        sorted_history = sorted(demand_history, key=lambda x: x.date)
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            sorted_history = [h for h in sorted_history if h.date >= cutoff_date]
        
        if not sorted_history:
            return 0.0
        
        total_demand = sum(h.quantity_consumed for h in sorted_history)
        days_range = (sorted_history[-1].date - sorted_history[0].date).days + 1
        
        return total_demand / max(1, days_range)
    
    def calculate_stock_coverage(self, current_stock: float,
                                average_daily_demand: float) -> Optional[float]:
        """
        Calculate how many days current stock will last.
        
        Returns:
            Days of coverage, or None if cannot calculate
        """
        if average_daily_demand <= 0:
            return None
        if current_stock < 0:
            return 0
        return current_stock / average_daily_demand
    
    def get_stock_status(self, current_stock: float,
                        average_daily_demand: float,
                        coverage_days: Optional[float] = None) -> StockStatus:
        """
        Determine stock status based on current stock and demand.
        
        Returns:
            StockStatus enum value
        """
        if coverage_days is None:
            coverage_days = self.calculate_stock_coverage(
                current_stock, average_daily_demand
            )
        
        if coverage_days is None:
            return StockStatus.UNKNOWN
        
        if current_stock <= 0:
            return StockStatus.STOCKOUT
        elif coverage_days <= self.critical_stock_days:
            return StockStatus.CRITICAL_STOCK
        elif coverage_days <= self.low_stock_days:
            return StockStatus.LOW_STOCK
        elif coverage_days >= self.overstock_days:
            return StockStatus.OVERSTOCKED
        else:
            return StockStatus.HEALTHY
    
    def detect_anomalies(self, demand_history: List[DemandHistory],
                        z_score_threshold: float = 2.5) -> Dict[str, List[DemandHistory]]:
        """
        Detect anomalies in demand using Z-score method.
        
        Returns:
            Dict with 'anomalies' and 'normal' lists
        """
        if len(demand_history) < 10:
            return {'anomalies': [], 'normal': demand_history, 'threshold': z_score_threshold}
        
        demands = [h.quantity_consumed for h in demand_history]
        mean = statistics.mean(demands)
        std = statistics.stdev(demands) if len(demands) > 1 else 0
        
        if std == 0:
            return {'anomalies': [], 'normal': demand_history, 'threshold': z_score_threshold}
        
        anomalies = []
        normal = []
        for entry in demand_history:
            z_score = abs(entry.quantity_consumed - mean) / std
            if z_score > z_score_threshold:
                anomalies.append(entry)
            else:
                normal.append(entry)
        
        return {
            'anomalies': anomalies,
            'normal': normal,
            'threshold': z_score_threshold,
            'mean': mean,
            'std': std
        }
    
    def calculate_wastage_rate(self, movements: List[StockMovement]) -> float:
        """
        Calculate wastage rate from stock movements.
        
        Returns:
            Wastage rate as percentage
        """
        total_waste = sum(m.quantity_wasted for m in movements)
        total_used_or_received = sum(
            m.quantity_used + m.quantity_received for m in movements
        )
        
        if total_used_or_received == 0:
            return 0.0
        
        return (total_waste / total_used_or_received) * 100
    
    def identify_expiring_items(self, stock_levels: List[StockLevel],
                               item_shelf_life: Dict[str, int],
                               days_threshold: int = 3) -> List[StockLevel]:
        """
        Identify items that are near expiry.
        
        Args:
            stock_levels: Current stock levels
            item_shelf_life: Dict mapping item_id to shelf life in days
            days_threshold: Days within which item expires
        
        Returns:
            List of stock levels for expiring items
        """
        expiring = []
        for stock in stock_levels:
            shelf_life = item_shelf_life.get(stock.item_id, 0)
            # Simulate expiry detection based on stock age
            # In real system, would use actual expiry dates
            if shelf_life > 0 and stock.current_quantity > 0:
                # Simulate some items being near expiry
                if stock.current_quantity % 10 == 0:
                    expiring.append(stock)
        return expiring