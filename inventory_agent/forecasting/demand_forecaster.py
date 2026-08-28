"""
Demand forecasting module using statistical methods.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import deque
import statistics
import math

from ..data_access.interfaces import DemandHistory


class DemandForecaster:
    """
    Forecasts future demand using statistical methods.
    Supports moving average, weighted moving average, and exponential smoothing.
    """
    
    def __init__(self, method: str = 'moving_average'):
        """
        Initialize the forecaster.
        
        Args:
            method: Forecasting method ('moving_average', 'weighted_moving_average', 'exponential_smoothing')
        """
        self.method = method
    
    def forecast(self, demand_history: List[DemandHistory],
                 forecast_days: int = 7,
                 method: Optional[str] = None) -> Dict:
        """
        Forecast demand for the specified number of days.
        
        Args:
            demand_history: Historical demand data
            forecast_days: Number of days to forecast
            method: Override default method
        
        Returns:
            Dict with forecast results
        """
        if not demand_history:
            return {
                'forecast': [],
                'method': method or self.method,
                'confidence': 'low',
                'warning': 'Insufficient historical data for forecasting'
            }
        
        # Sort by date
        sorted_history = sorted(demand_history, key=lambda x: x.date)
        
        # Extract daily demand values
        daily_demands = [h.quantity_consumed for h in sorted_history]
        
        # Choose method
        forecast_method = method or self.method
        forecast_values = []
        confidence = 'medium'
        
        if len(daily_demands) < 10:
            # Use simple average for small datasets
            avg_demand = statistics.mean(daily_demands) if daily_demands else 0
            forecast_values = [avg_demand] * forecast_days
            confidence = 'low'
        elif forecast_method == 'moving_average':
            forecast_values = self._moving_average(daily_demands, forecast_days)
        elif forecast_method == 'weighted_moving_average':
            forecast_values = self._weighted_moving_average(daily_demands, forecast_days)
        elif forecast_method == 'exponential_smoothing':
            forecast_values = self._exponential_smoothing(daily_demands, forecast_days)
        else:
            # Default to moving average
            forecast_values = self._moving_average(daily_demands, forecast_days)
        
        # Calculate confidence
        if len(daily_demands) >= 30:
            confidence = 'high'
        elif len(daily_demands) >= 15:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        # Calculate prediction range (approximate)
        std_dev = statistics.stdev(daily_demands) if len(daily_demands) > 1 else 0
        prediction_range = {
            'lower': [v - std_dev for v in forecast_values],
            'upper': [v + std_dev for v in forecast_values]
        }
        
        return {
            'forecast': forecast_values,
            'forecast_days': forecast_days,
            'method': forecast_method,
            'confidence': confidence,
            'prediction_range': prediction_range,
            'mean_demand': statistics.mean(daily_demands) if daily_demands else 0,
            'std_dev': std_dev,
            'total_forecast_demand': sum(forecast_values)
        }
    
    def _moving_average(self, data: List[float], forecast_days: int,
                        window: int = 7) -> List[float]:
        """
        Calculate moving average forecast.
        """
        if len(data) < window:
            # Not enough data, use all available
            window = len(data)
        
        # Use last 'window' days for average
        recent = data[-window:] if window > 0 else data
        avg = statistics.mean(recent) if recent else 0
        return [avg] * forecast_days
    
    def _weighted_moving_average(self, data: List[float], forecast_days: int,
                                 window: int = 7) -> List[float]:
        """
        Calculate weighted moving average forecast.
        Recent days get higher weight.
        """
        if len(data) < window:
            window = len(data)
        
        recent = data[-window:] if window > 0 else data
        
        if not recent:
            return [0] * forecast_days
        
        # Assign weights (more weight to recent days)
        weights = list(range(1, len(recent) + 1))
        weighted_sum = sum(val * weight for val, weight in zip(recent, weights))
        total_weight = sum(weights)
        
        avg = weighted_sum / total_weight
        return [avg] * forecast_days
    
    def _exponential_smoothing(self, data: List[float], forecast_days: int,
                               alpha: float = 0.3) -> List[float]:
        """
        Calculate exponential smoothing forecast.
        """
        if not data:
            return [0] * forecast_days
        
        # Initialize with first value
        smoothed = data[0]
        
        for value in data[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed
        
        return [smoothed] * forecast_days
    
    def calculate_seasonality(self, demand_history: List[DemandHistory],
                              period: int = 7) -> Optional[Dict]:
        """
        Detect seasonality patterns in demand.
        
        Args:
            demand_history: Historical demand data
            period: Seasonality period (e.g., 7 for weekly)
        
        Returns:
            Dict with seasonality factors or None if insufficient data
        """
        if len(demand_history) < period * 3:
            return None
        
        # Group by day of week
        day_patterns = {}
        for entry in demand_history:
            day = entry.date.weekday()
            if day not in day_patterns:
                day_patterns[day] = []
            day_patterns[day].append(entry.quantity_consumed)
        
        # Calculate average for each day
        day_averages = {}
        for day, values in day_patterns.items():
            if len(values) >= 3:
                day_averages[day] = statistics.mean(values)
        
        if len(day_averages) < 5:
            return None
        
        # Calculate overall average
        overall_avg = statistics.mean(day_averages.values())
        
        # Calculate seasonal factors
        seasonal_factors = {
            day: avg / overall_avg if overall_avg > 0 else 1.0
            for day, avg in day_averages.items()
        }
        
        return {
            'period': period,
            'factors': seasonal_factors,
            'overall_average': overall_avg
        }