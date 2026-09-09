import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

class WorkforceAnalytics:
    """Deterministic analytics for workforce data"""
    
    def __init__(self, data_provider):
        self.data_provider = data_provider
    
    def calculate_attendance_metrics(self, staff_id: str = None, outlet_id: str = None) -> Dict:
        """Calculate attendance metrics"""
        df = self.data_provider.get_attendance()
        
        if staff_id:
            df = df[df['staff_id'] == staff_id]
        if outlet_id:
            df = df[df['outlet_id'] == outlet_id]
        
        if len(df) == 0:
            return {"error": "No attendance data found"}
        
        total_days = len(df)
        present_days = len(df[df['attendance_status'] == 'Present'])
        absent_days = len(df[df['attendance_status'] == 'Absent'])
        late_days = len(df[df['attendance_status'] == 'Late'])
        
        attendance_rate = round((present_days / total_days) * 100, 1) if total_days > 0 else 0
        
        return {
            "total_days": total_days,
            "present_days": present_days,
            "absent_days": absent_days,
            "late_days": late_days,
            "attendance_rate": attendance_rate,
            "avg_late_minutes": round(df['late_minutes'].mean(), 1) if 'late_minutes' in df else 0,
            "total_overtime": round(df['overtime_hours'].sum(), 1) if 'overtime_hours' in df else 0,
            "avg_overtime": round(df['overtime_hours'].mean(), 1) if 'overtime_hours' in df else 0
        }
    
    def calculate_productivity(self, staff_id: str = None, outlet_id: str = None) -> Dict:
        """Calculate productivity metrics"""
        df = self.data_provider.get_performance()
        
        if staff_id:
            df = df[df['staff_id'] == staff_id]
        if outlet_id:
            df = df[df['outlet_id'] == outlet_id]
        
        if len(df) == 0:
            return {"error": "No performance data found"}
        
        metrics = {
            "avg_tasks_completed": round(df['tasks_completed'].mean(), 1) if 'tasks_completed' in df else 0,
            "avg_sales_generated": round(df['sales_generated'].mean(), 1) if 'sales_generated' in df else 0,
            "avg_productivity_score": round(df['productivity_score'].mean(), 2) if 'productivity_score' in df else 0,
            "avg_customers_served": round(df['customer_served'].mean(), 1) if 'customer_served' in df else 0,
            "avg_working_hours": round(df['working_hours'].mean(), 1) if 'working_hours' in df else 0,
            "total_tasks": df['tasks_completed'].sum() if 'tasks_completed' in df else 0
        }
        
        # Calculate trends
        if 'date' in df and len(df) > 1:
            df_sorted = df.sort_values('date')
            if 'productivity_score' in df:
                recent_avg = df_sorted.tail(7)['productivity_score'].mean()
                previous_avg = df_sorted.head(len(df_sorted) - 7)['productivity_score'].mean() if len(df_sorted) > 7 else df_sorted['productivity_score'].mean()
                metrics["trend"] = "increasing" if recent_avg > previous_avg else "decreasing" if recent_avg < previous_avg else "stable"
                metrics["trend_percentage"] = round(((recent_avg - previous_avg) / previous_avg) * 100, 1) if previous_avg > 0 else 0
        
        return metrics
    
    def analyze_staffing_levels(self) -> Dict:
        """Analyze staffing levels across outlets"""
        staff_df = self.data_provider.get_staff()
        schedule_df = self.data_provider.get_schedules()
        attendance_df = self.data_provider.get_attendance()
        
        outlets = staff_df['outlet_id'].unique()
        results = {}
        
        for outlet in outlets:
            total_staff = len(staff_df[staff_df['outlet_id'] == outlet])
            scheduled = len(schedule_df[schedule_df['outlet_id'] == outlet])
            present = len(attendance_df[(attendance_df['outlet_id'] == outlet) & 
                                      (attendance_df['attendance_status'] == 'Present')])
            
            # Estimate required staff (simple heuristic: 1 per 2 scheduled hours)
            # In reality, this would be more sophisticated
            required_staff = max(3, min(10, scheduled // 2))
            
            shortage = required_staff - scheduled
            overstaffed = scheduled - required_staff
            
            results[outlet] = {
                "total_staff": total_staff,
                "scheduled_today": scheduled,
                "present_today": present,
                "required_estimate": required_staff,
                "shortage": shortage if shortage > 0 else 0,
                "overstaffed": overstaffed if overstaffed > 0 else 0,
                "status": "UNDERSTAFFED" if shortage > 0 else "OVERSTAFFED" if overstaffed > 0 else "OPTIMAL"
            }
        
        return results
    
    def detect_anomalies(self) -> List[Dict]:
        """Detect workforce anomalies using statistical methods"""
        anomalies = []
        
        # Check attendance anomalies
        attendance_df = self.data_provider.get_attendance()
        if len(attendance_df) > 0:
            # Detect high absenteeism
            staff_attendance = attendance_df.groupby('staff_id').agg({
                'attendance_status': lambda x: (x == 'Absent').sum() / len(x) * 100
            }).reset_index()
            
            high_absentee = staff_attendance[staff_attendance['attendance_status'] > 20]
            for _, row in high_absentee.iterrows():
                anomalies.append({
                    "type": "High Absenteeism",
                    "staff_id": row['staff_id'],
                    "details": f"Absenteeism rate: {row['attendance_status']:.1f}%",
                    "severity": "High" if row['attendance_status'] > 30 else "Medium"
                })
            
            # Detect high overtime
            if 'overtime_hours' in attendance_df.columns:
                staff_overtime = attendance_df.groupby('staff_id')['overtime_hours'].sum().reset_index()
                high_overtime = staff_overtime[staff_overtime['overtime_hours'] > 20]
                for _, row in high_overtime.iterrows():
                    anomalies.append({
                        "type": "High Overtime",
                        "staff_id": row['staff_id'],
                        "details": f"Total overtime: {row['overtime_hours']:.1f} hours",
                        "severity": "High" if row['overtime_hours'] > 40 else "Medium"
                    })
        
        # Detect performance anomalies
        perf_df = self.data_provider.get_performance()
        if len(perf_df) > 0 and 'productivity_score' in perf_df.columns:
            # Detect sudden productivity drops
            staff_prod = perf_df.groupby('staff_id')['productivity_score'].agg(['mean', 'std']).reset_index()
            staff_prod.columns = ['staff_id', 'mean_prod', 'std_prod']
            
            for _, row in staff_prod.iterrows():
                if row['std_prod'] > 0.2:  # High variance
                    anomalies.append({
                        "type": "Inconsistent Productivity",
                        "staff_id": row['staff_id'],
                        "details": f"Productivity variance: {row['std_prod']:.2f}",
                        "severity": "Medium"
                    })
        
        return anomalies
    
    def forecast_staffing(self, days_ahead: int = 7) -> Dict:
        """Simple staffing forecast based on historical patterns"""
        schedule_df = self.data_provider.get_schedules()
        attendance_df = self.data_provider.get_attendance()
        
        if len(schedule_df) == 0 or len(attendance_df) == 0:
            return {"error": "Insufficient data for forecasting"}
        
        # Get current date
        today = datetime.now()
        
        # Find typical staffing patterns by day of week
        schedule_df['date'] = pd.to_datetime(schedule_df['date'])
        schedule_df['day_of_week'] = schedule_df['date'].dt.dayofweek
        day_pattern = schedule_df.groupby('day_of_week').size().reset_index(name='avg_scheduled')
        day_pattern['avg_scheduled'] = day_pattern['avg_scheduled'] / len(schedule_df['date'].dt.date.unique())
        
        # Find typical attendance rates by day
        attendance_df['date'] = pd.to_datetime(attendance_df['date'])
        attendance_df['day_of_week'] = attendance_df['date'].dt.dayofweek
        attendance_pattern = attendance_df.groupby('day_of_week').apply(
            lambda x: (x['attendance_status'] == 'Present').sum() / len(x) * 100
        ).reset_index(name='attendance_rate')
        
        forecast = {}
        for i in range(days_ahead):
            forecast_date = today + timedelta(days=i)
            day_num = forecast_date.weekday()
            
            # Get expected staffing from pattern
            expected_staff = day_pattern[day_pattern['day_of_week'] == day_num]
            expected_count = int(expected_staff['avg_scheduled'].iloc[0]) if len(expected_staff) > 0 else 0
            
            # Expected attendance
            expected_att = attendance_pattern[attendance_pattern['day_of_week'] == day_num]
            attendance_rate = expected_att['attendance_rate'].iloc[0] if len(expected_att) > 0 else 80
            
            expected_present = int(expected_count * (attendance_rate / 100))
            
            forecast[forecast_date.strftime("%Y-%m-%d")] = {
                "day": forecast_date.strftime("%A"),
                "expected_scheduled": expected_count,
                "expected_attendance_rate": round(attendance_rate, 1),
                "expected_present": expected_present,
                "confidence": "Medium"  # Simplified
            }
        
        return forecast