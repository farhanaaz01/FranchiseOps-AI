"""
Inventory Agent for FranchiseOps AI.
"""

from .agent.inventory_agent import InventoryAgent
from .data_access.csv_provider import CSVDataProvider
from .data_access.interfaces import (
    DataAccessInterface,
    InventoryItem,
    StockLevel,
    StockMovement,
    DemandHistory,
    SupplierInfo
)
from .config.settings import settings

__version__ = "1.0.0"
__all__ = [
    'InventoryAgent',
    'CSVDataProvider',
    'DataAccessInterface',
    'InventoryItem',
    'StockLevel',
    'StockMovement',
    'DemandHistory',
    'SupplierInfo',
    'settings'
]