"""
Analytics calculations for the Outlet Performance Agent
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from collections import defaultdict
import logging

from ..models.data_models import SalesRecord, Outlet, HealthScore, HealthScoreBreakdown

logger = logging.getLogger(__name__)


class RevenueAnalyzer:
    """Revenue analysis calculations"""
    
    @staticmethod
    def total_revenue(sales: List[SalesRecord]) -> float:
        """Calculate total revenue from sales records"""
        return sum(s.revenue for s in sales if s.revenue is not None)
    
    @staticmethod
    def average_revenue(sales: List[SalesRecord]) -> float:
        """Calculate average revenue per day"""
        revenues = [s.revenue for s in sales if s.revenue is not None]
        if not revenues:
            return 0.0
        return sum(revenues) / len(revenues)
    
    @staticmethod
    def daily_revenue(sales: List[SalesRecord]) -> Dict[date, float]:
        """Get daily revenue breakdown"""
        daily = defaultdict(float)
        for sale in sales:
            if sale.revenue is not None:
                daily[sale.date] += sale.revenue
        return dict(daily)
    
    @staticmethod
    def weekly_revenue(sales: List[SalesRecord]) -> Dict[str, float]:
        """Get weekly revenue breakdown"""
        weekly = defaultdict(float)
        for sale in sales:
            if sale.revenue is not None:
                # ISO week number
                week_key = f"{sale.date.year}-W{sale.date.isocalendar()[1]:02d}"
                weekly[week_key] += sale.revenue
        return dict(weekly)
    
    @staticmethod
    def monthly_revenue(sales: List[SalesRecord]) -> Dict[str, float]:
        """Get monthly revenue breakdown"""
        monthly = defaultdict(float)
        for sale in sales:
            if sale.revenue is not None:
                month_key = f"{sale.date.year}-{sale.date.month:02d}"
                monthly[month_key] += sale.revenue
        return dict(monthly)
    
    @staticmethod
    def revenue_growth(sales: List[SalesRecord], 
                      periods: int = 30) -> Optional[float]:
        """Calculate revenue growth over specified period"""
        if len(sales) < 2:
            return None
        
        # Sort by date
        sorted_sales = sorted(sales, key=lambda x: x.date)
        
        # Get revenue by date
        daily = RevenueAnalyzer.daily_revenue(sorted_sales)
        dates = sorted(daily.keys())
        
        if len(dates) < 2:
            return None
        
        # Compare first and last period
        mid_point = len(dates) // 2
        first_half = [daily[d] for d in dates[:mid_point]]
        second_half = [daily[d] for d in dates[mid_point:]]
        
        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0
        
        if avg_first == 0:
            return None
        
        return ((avg_second - avg_first) / avg_first) * 100
    
    @staticmethod
    def revenue_percentage_change(current: float, previous: float) -> float:
        """Calculate percentage change between two values"""
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100


class SalesAnalyzer:
    """Sales analysis calculations"""
    
    @staticmethod
    def transaction_count(sales: List[SalesRecord]) -> int:
        """Total transaction count"""
        return sum(s.transaction_count for s in sales if s.transaction_count is not None)
    
    @staticmethod
    def average_order_value(sales: List[SalesRecord]) -> Optional[float]:
        """Calculate average order value"""
        aovs = [s.average_order_value for s in sales if s.average_order_value is not None]
        if not aovs:
            return None
        return sum(aovs) / len(aovs)
    
    @staticmethod
    def customer_count(sales: List[SalesRecord]) -> int:
        """Total customer count"""
        return sum(s.customer_count for s in sales if s.customer_count is not None)


class TrendAnalyzer:
    """Trend analysis calculations"""
    
    @staticmethod
    def detect_trend(sales: List[SalesRecord], threshold: float = 5.0) -> str:
        """
        Detect if sales trend is increasing, decreasing, or stable
        
        Args:
            sales: List of sales records
            threshold: Percentage change threshold to detect significant change
        
        Returns:
            "increasing", "decreasing", "stable", or "unknown"
        """
        if len(sales) < 7:  # Need at least a week of data
            return "unknown"
        
        # Sort by date
        sorted_sales = sorted(sales, key=lambda x: x.date)
        
        # Get daily revenue
        daily_revenue = defaultdict(float)
        for sale in sorted_sales:
            if sale.revenue is not None:
                daily_revenue[sale.date] += sale.revenue
        
        dates = sorted(daily_revenue.keys())
        if len(dates) < 7:
            return "unknown"
        
        revenues = [daily_revenue[d] for d in dates]
        
        # Calculate simple linear regression slope
        x = np.arange(len(revenues))
        y = np.array(revenues)
        
        if len(y) < 2:
            return "unknown"
        
        slope, _ = np.polyfit(x, y, 1)
        
        # Calculate percentage change relative to mean
        mean_revenue = np.mean(y)
        if mean_revenue == 0:
            return "stable"
        
        # Normalize slope by mean
        normalized_slope = (slope / mean_revenue) * 100
        
        if normalized_slope > threshold:
            return "increasing"
        elif normalized_slope < -threshold:
            return "decreasing"
        else:
            return "stable"
    
    @staticmethod
    def consecutive_declines(sales: List[SalesRecord], days: int = 7) -> int:
        """Count consecutive days of revenue decline"""
        if len(sales) < 2:
            return 0
        
        sorted_sales = sorted(sales, key=lambda x: x.date)
        daily_revenue = defaultdict(float)
        for sale in sorted_sales:
            if sale.revenue is not None:
                daily_revenue[sale.date] += sale.revenue
        
        dates = sorted(daily_revenue.keys())
        if len(dates) < 2:
            return 0
        
        declines = 0
        for i in range(1, len(dates)):
            if daily_revenue[dates[i]] < daily_revenue[dates[i-1]]:
                declines += 1
            else:
                declines = 0  # Reset on increase
        
        return declines
    
    @staticmethod
    def detect_anomalies(sales: List[SalesRecord], 
                         z_threshold: float = 3.0) -> List[Dict[str, Any]]:
        """
        Detect revenue anomalies using Z-score method
        
        Args:
            sales: List of sales records
            z_threshold: Z-score threshold for anomaly detection
        
        Returns:
            List of anomaly records with date and revenue
        """
        if len(sales) < 7:
            return []
        
        daily_revenue = defaultdict(float)
        for sale in sales:
            if sale.revenue is not None:
                daily_revenue[sale.date] += sale.revenue
        
        revenues = list(daily_revenue.values())
        dates = list(daily_revenue.keys())
        
        if len(revenues) < 7:
            return []
        
        mean_revenue = np.mean(revenues)
        std_revenue = np.std(revenues)
        
        if std_revenue == 0:
            return []
        
        anomalies = []
        for date_val, revenue in zip(dates, revenues):
            z_score = (revenue - mean_revenue) / std_revenue
            if abs(z_score) > z_threshold:
                anomalies.append({
                    "date": date_val,
                    "revenue": revenue,
                    "z_score": z_score,
                    "type": "high" if z_score > 0 else "low"
                })
        
        return anomalies


class HealthScoreCalculator:
    """Outlet health score calculation with configurable weights"""
    
    def __init__(self, 
                 weight_revenue: float = 0.30,
                 weight_growth: float = 0.25,
                 weight_sales_volume: float = 0.20,
                 weight_trend_consistency: float = 0.15,
                 weight_peer_performance: float = 0.10):
        """
        Initialize with configurable weights
        
        Args:
            weight_revenue: Weight for revenue performance (0-1)
            weight_growth: Weight for growth metric (0-1)
            weight_sales_volume: Weight for sales volume (0-1)
            weight_trend_consistency: Weight for trend consistency (0-1)
            weight_peer_performance: Weight for peer comparison (0-1)
        """
        total = weight_revenue + weight_growth + weight_sales_volume + \
                weight_trend_consistency + weight_peer_performance
        
        if not (0.99 <= total <= 1.01):
            logger.warning(f"Weights sum to {total}, normalizing to 1.0")
            # Normalize weights
            self.weights = {
                "revenue": weight_revenue / total,
                "growth": weight_growth / total,
                "sales_volume": weight_sales_volume / total,
                "trend_consistency": weight_trend_consistency / total,
                "peer_performance": weight_peer_performance / total
            }
        else:
            self.weights = {
                "revenue": weight_revenue,
                "growth": weight_growth,
                "sales_volume": weight_sales_volume,
                "trend_consistency": weight_trend_consistency,
                "peer_performance": weight_peer_performance
            }
        
        self.score_thresholds = {
            "EXCELLENT": 85,
            "GOOD": 70,
            "STABLE": 55,
            "AT_RISK": 40,
            "UNDERPERFORMING": 25,
            "CRITICAL": 0
        }
    
    def calculate_health_score(self,
                               outlet_id: str,
                               sales: List[SalesRecord],
                               all_outlets: List[Outlet] = None,
                               peer_sales: Dict[str, List[SalesRecord]] = None) -> HealthScore:
        """
        Calculate comprehensive health score for an outlet
        """
        if not sales:
            return HealthScore(
                outlet_id=outlet_id,
                score=0,
                category="CRITICAL",
                explanation="No sales data available for this outlet"
            )
        
        # Calculate component scores (0-100)
        revenue_score = self._calculate_revenue_score(sales)
        growth_score = self._calculate_growth_score(sales)
        sales_volume_score = self._calculate_sales_volume_score(sales)
        trend_score = self._calculate_trend_score(sales)
        peer_score = self._calculate_peer_score(outlet_id, sales, all_outlets, peer_sales)
        
        # Weighted total
        total_score = (
            revenue_score * self.weights["revenue"] +
            growth_score * self.weights["growth"] +
            sales_volume_score * self.weights["sales_volume"] +
            trend_score * self.weights["trend_consistency"] +
            peer_score * self.weights["peer_performance"]
        )
        
        # Ensure score is 0-100
        total_score = max(0, min(100, total_score))
        
        # Determine category
        category = self._get_category(total_score)
        
        # Create breakdown
        breakdown = HealthScoreBreakdown(
            revenue_performance=revenue_score,
            growth=growth_score,
            sales_volume=sales_volume_score,
            trend_consistency=trend_score,
            peer_performance=peer_score
        )
        
        # Generate explanation
        explanation = self._generate_explanation(outlet_id, total_score, category, breakdown)
        
        return HealthScore(
            outlet_id=outlet_id,
            score=total_score,
            category=category,
            breakdown=breakdown,
            explanation=explanation
        )
    
    def _calculate_revenue_score(self, sales: List[SalesRecord]) -> float:
        """Calculate revenue performance score"""
        if not sales:
            return 0
        
        total_revenue = sum(s.revenue for s in sales if s.revenue is not None)
        days = len([s for s in sales if s.revenue is not None])
        
        if days == 0:
            return 0
        
        avg_daily_revenue = total_revenue / days
        
        # Normalize score based on revenue (assuming healthy daily revenue is 5000+)
        # Using a sigmoid-like function
        score = min(100, (avg_daily_revenue / 5000) * 100)
        return score
    
    def _calculate_growth_score(self, sales: List[SalesRecord]) -> float:
        """Calculate growth performance score"""
        if len(sales) < 14:  # Need at least 2 weeks
            return 50  # Neutral score
        
        growth = RevenueAnalyzer.revenue_growth(sales, periods=30)
        
        if growth is None:
            return 50
        
        # Convert growth to score (-20% to +20% maps to 0-100)
        # Growth of 0% gives 50, +10% gives 75, -10% gives 25
        score = 50 + (growth * 2.5)  # 10% growth = 75, 10% decline = 25
        return max(0, min(100, score))
    
    def _calculate_sales_volume_score(self, sales: List[SalesRecord]) -> float:
        """Calculate sales volume score"""
        if not sales:
            return 0
        
        transactions = SalesAnalyzer.transaction_count(sales)
        days = len(sales)
        
        if days == 0:
            return 0
        
        avg_transactions = transactions / days
        
        # Normalize score (assuming healthy daily transactions is 50+)
        score = min(100, (avg_transactions / 50) * 100)
        return score
    
    def _calculate_trend_score(self, sales: List[SalesRecord]) -> float:
        """Calculate trend consistency score"""
        trend = TrendAnalyzer.detect_trend(sales)
        
        if trend == "increasing":
            return 90
        elif trend == "stable":
            return 70
        elif trend == "decreasing":
            return 30
        else:
            return 50
    
    def _calculate_peer_score(self,
                              outlet_id: str,
                              sales: List[SalesRecord],
                              all_outlets: List[Outlet],
                              peer_sales: Dict[str, List[SalesRecord]]) -> float:
        """Calculate peer performance score"""
        if not all_outlets or not peer_sales:
            return 50  # Neutral if no peer data
        
        # Calculate current outlet's average revenue
        my_avg = RevenueAnalyzer.average_revenue(sales)
        
        # Calculate peer averages
        peer_avgs = []
        for pid, psales in peer_sales.items():
            if pid != outlet_id:
                avg = RevenueAnalyzer.average_revenue(psales)
                if avg > 0:
                    peer_avgs.append(avg)
        
        if not peer_avgs:
            return 50
        
        avg_peer = sum(peer_avgs) / len(peer_avgs)
        
        if avg_peer == 0:
            return 50
        
        # Score based on ratio to peer average (0.5x = 50, 1.0x = 100)
        ratio = my_avg / avg_peer
        score = min(100, max(0, ratio * 100))
        return score
    
    def _get_category(self, score: float) -> str:
        """Get category based on score"""
        for category, threshold in self.score_thresholds.items():
            if score >= threshold:
                return category
        return "CRITICAL"
    
    def _generate_explanation(self, 
                              outlet_id: str, 
                              score: float, 
                              category: str,
                              breakdown: HealthScoreBreakdown) -> str:
        """Generate human-readable explanation"""
        explanations = []
        explanations.append(f"Outlet {outlet_id} received {score:.1f}/100, categorized as {category}.")
        
        if breakdown.revenue_performance < 50:
            explanations.append("Revenue performance is below target.")
        elif breakdown.revenue_performance >= 80:
            explanations.append("Revenue performance is strong.")
        
        if breakdown.growth < 40:
            explanations.append("Growth is a concern.")
        elif breakdown.growth >= 80:
            explanations.append("Growth is excellent.")
        
        if breakdown.trend_consistency < 40:
            explanations.append("Trend consistency is poor.")
        
        if breakdown.peer_performance < 40:
            explanations.append("Performing below peers.")
        
        return " ".join(explanations)


class OutletComparator:
    """Outlet comparison utilities"""
    
    @staticmethod
    def compare_outlets(sales_data: Dict[str, List[SalesRecord]],
                        metric: str = "revenue") -> List[Dict[str, Any]]:
        """
        Compare outlets based on specified metric
        
        Args:
            sales_data: Dict mapping outlet_id to list of sales records
            metric: "revenue", "growth", "transactions", "aov"
        
        Returns:
            List of outlets with their metric values, sorted by performance
        """
        results = []
        
        for outlet_id, sales in sales_data.items():
            if not sales:
                continue
            
            if metric == "revenue":
                value = RevenueAnalyzer.total_revenue(sales)
            elif metric == "growth":
                value = RevenueAnalyzer.revenue_growth(sales)
                if value is None:
                    value = 0
            elif metric == "transactions":
                value = SalesAnalyzer.transaction_count(sales)
            elif metric == "aov":
                value = SalesAnalyzer.average_order_value(sales)
                if value is None:
                    value = 0
            else:
                value = RevenueAnalyzer.total_revenue(sales)
            
            results.append({
                "outlet_id": outlet_id,
                "metric": metric,
                "value": value
            })
        
        # Sort by value descending
        results.sort(key=lambda x: x["value"], reverse=True)
        
        # Add ranks
        for i, result in enumerate(results):
            result["rank"] = i + 1
        
        return results