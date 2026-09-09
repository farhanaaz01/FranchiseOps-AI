import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    LLM_MODEL = "gemini-1.5-flash"  # Free version
    USE_LLM = bool(GOOGLE_API_KEY)
    
    # Data paths
    DATA_DIR = "staff_agent/data"
    STAFF_FILE = f"{DATA_DIR}/staff.csv"
    ATTENDANCE_FILE = f"{DATA_DIR}/attendance.csv"
    SCHEDULE_FILE = f"{DATA_DIR}/schedule.csv"
    PERFORMANCE_FILE = f"{DATA_DIR}/performance.csv"