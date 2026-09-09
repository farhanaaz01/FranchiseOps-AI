import pandas as pd
import os
from datetime import datetime, timedelta
import random
from typing import List, Dict, Optional, Any

class DataProvider:
    """Data access layer for Staff Agent - independent of backend"""
    
    def __init__(self, data_dir: str = "staff_agent/data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self._ensure_sample_data()
    
    def _ensure_sample_data(self):
        """Create sample data if files don't exist"""
        if not os.path.exists(f"{self.data_dir}/staff.csv"):
            self._create_sample_staff()
        if not os.path.exists(f"{self.data_dir}/attendance.csv"):
            self._create_sample_attendance()
        if not os.path.exists(f"{self.data_dir}/schedule.csv"):
            self._create_sample_schedule()
        if not os.path.exists(f"{self.data_dir}/performance.csv"):
            self._create_sample_performance()
    
    def _create_sample_staff(self):
        """Create sample staff data"""
        staff = [
            {"staff_id": "S001", "staff_name": "Rahul Sharma", "outlet_id": "OUT001", "role": "Cashier", "department": "Frontend", "employment_status": "Active", "joining_date": "2023-01-15"},
            {"staff_id": "S002", "staff_name": "Priya Patel", "outlet_id": "OUT001", "role": "Cleaner", "department": "Facilities", "employment_status": "Active", "joining_date": "2023-02-01"},
            {"staff_id": "S003", "staff_name": "Amit Singh", "outlet_id": "OUT001", "role": "Manager", "department": "Management", "employment_status": "Active", "joining_date": "2022-11-01"},
            {"staff_id": "S004", "staff_name": "Neha Gupta", "outlet_id": "OUT002", "role": "Cashier", "department": "Frontend", "employment_status": "Active", "joining_date": "2023-03-15"},
            {"staff_id": "S005", "staff_name": "Vikram Reddy", "outlet_id": "OUT002", "role": "Cook", "department": "Kitchen", "employment_status": "Active", "joining_date": "2023-01-20"},
            {"staff_id": "S006", "staff_name": "Deepa Nair", "outlet_id": "OUT003", "role": "Cashier", "department": "Frontend", "employment_status": "Active", "joining_date": "2023-04-01"},
            {"staff_id": "S007", "staff_name": "Ravi Kumar", "outlet_id": "OUT003", "role": "Cleaner", "department": "Facilities", "employment_status": "Active", "joining_date": "2023-02-15"},
            {"staff_id": "S008", "staff_name": "Sneha Menon", "outlet_id": "OUT003", "role": "Manager", "department": "Management", "employment_status": "Active", "joining_date": "2022-12-01"},
            {"staff_id": "S009", "staff_name": "Arjun Das", "outlet_id": "OUT004", "role": "Cook", "department": "Kitchen", "employment_status": "Active", "joining_date": "2023-01-10"},
            {"staff_id": "S010", "staff_name": "Meera Iyer", "outlet_id": "OUT004", "role": "Cashier", "department": "Frontend", "employment_status": "Active", "joining_date": "2023-03-01"},
        ]
        df = pd.DataFrame(staff)
        df.to_csv(f"{self.data_dir}/staff.csv", index=False)
    
    def _create_sample_attendance(self):
        """Create sample attendance data for last 30 days"""
        staff_ids = [f"S{str(i).zfill(3)}" for i in range(1, 11)]
        outlet_ids = ["OUT001", "OUT002", "OUT003", "OUT004"]
        data = []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for staff_id in staff_ids:
            outlet_id = random.choice(outlet_ids)
            for day in range(30):
                date = start_date + timedelta(days=day)
                # Skip weekends sometimes
                if date.weekday() >= 5 and random.random() < 0.3:
                    continue
                
                scheduled = 8 + random.choice([-1, 0, 1])
                actual = scheduled - random.randint(0, 2)
                status = "Present" if actual >= scheduled * 0.8 else "Absent" if actual < 2 else "Late"
                late_minutes = random.randint(0, 30) if status == "Late" else 0
                overtime = random.randint(0, 2) if random.random() < 0.3 else 0
                
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "staff_id": staff_id,
                    "outlet_id": outlet_id,
                    "scheduled_hours": scheduled,
                    "actual_hours": actual,
                    "attendance_status": status,
                    "late_minutes": late_minutes,
                    "overtime_hours": overtime
                })
        
        df = pd.DataFrame(data)
        df.to_csv(f"{self.data_dir}/attendance.csv", index=False)
    
    def _create_sample_schedule(self):
        """Create sample schedule data"""
        staff_ids = [f"S{str(i).zfill(3)}" for i in range(1, 11)]
        data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        shifts = [
            {"start": "08:00", "end": "16:00", "type": "Morning"},
            {"start": "16:00", "end": "00:00", "type": "Evening"},
            {"start": "00:00", "end": "08:00", "type": "Night"}
        ]
        
        for staff_id in staff_ids:
            for day in range(7):
                date = start_date + timedelta(days=day)
                shift = random.choice(shifts)
                data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "staff_id": staff_id,
                    "outlet_id": f"OUT{str(random.randint(1, 4)).zfill(3)}",
                    "shift_start": shift["start"],
                    "shift_end": shift["end"],
                    "scheduled_hours": 8,
                    "shift_type": shift["type"]
                })
        
        df = pd.DataFrame(data)
        df.to_csv(f"{self.data_dir}/schedule.csv", index=False)
    
    def _create_sample_performance(self):
        """Create sample performance data"""
        staff_ids = [f"S{str(i).zfill(3)}" for i in range(1, 11)]
        data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for staff_id in staff_ids:
            for day in range(30):
                date = start_date + timedelta(days=day)
                if random.random() < 0.2:  # Not every day has performance data
                    continue
                data.append({
                    "staff_id": staff_id,
                    "outlet_id": f"OUT{str(random.randint(1, 4)).zfill(3)}",
                    "date": date.strftime("%Y-%m-%d"),
                    "tasks_completed": random.randint(5, 20),
                    "sales_generated": random.randint(100, 500) if random.random() < 0.5 else 0,
                    "productivity_score": round(random.uniform(0.5, 1.0), 2),
                    "customer_served": random.randint(10, 50),
                    "working_hours": random.randint(6, 10)
                })
        
        df = pd.DataFrame(data)
        df.to_csv(f"{self.data_dir}/performance.csv", index=False)
    
    def get_staff(self) -> pd.DataFrame:
        """Get all staff data"""
        return pd.read_csv(f"{self.data_dir}/staff.csv")
    
    def get_staff_member(self, staff_id: str) -> Optional[Dict]:
        """Get specific staff member"""
        df = self.get_staff()
        record = df[df['staff_id'] == staff_id]
        if len(record) == 0:
            return None
        return record.iloc[0].to_dict()
    
    def get_attendance(self) -> pd.DataFrame:
        """Get attendance data"""
        return pd.read_csv(f"{self.data_dir}/attendance.csv")
    
    def get_schedules(self) -> pd.DataFrame:
        """Get schedule data"""
        return pd.read_csv(f"{self.data_dir}/schedule.csv")
    
    def get_performance(self) -> pd.DataFrame:
        """Get performance data"""
        return pd.read_csv(f"{self.data_dir}/performance.csv")
    
    def get_outlet_staffing(self, outlet_id: str) -> pd.DataFrame:
        """Get staffing data for specific outlet"""
        staff = self.get_staff()
        return staff[staff['outlet_id'] == outlet_id]