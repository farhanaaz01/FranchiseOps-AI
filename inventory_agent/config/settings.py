"""
Configuration settings for the Inventory Agent.
Uses environment variables for sensitive configuration.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""
    
    # LLM Configuration
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    
    # Data paths
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    # Sample data files
    INVENTORY_FILE: str = os.path.join(DATA_DIR, "inventory.csv")
    MOVEMENTS_FILE: str = os.path.join(DATA_DIR, "movements.csv")
    DEMAND_FILE: str = os.path.join(DATA_DIR, "demand_history.csv")
    SUPPLIERS_FILE: str = os.path.join(DATA_DIR, "suppliers.csv")
    OUTLETS_FILE: str = os.path.join(DATA_DIR, "outlets.csv")
    
    # Thresholds
    LOW_STOCK_THRESHOLD_DAYS: int = 3
    CRITICAL_STOCK_THRESHOLD_DAYS: int = 1
    OVERSTOCK_THRESHOLD_DAYS: int = 14
    WASTAGE_THRESHOLD_PERCENT: float = 5.0
    
    # Forecasting defaults
    DEFAULT_FORECAST_DAYS: int = 7
    MIN_HISTORY_DAYS: int = 14
    
    @property
    def has_api_key(self) -> bool:
        """Check if API key is available."""
        return bool(self.GOOGLE_API_KEY)


settings = Settings()