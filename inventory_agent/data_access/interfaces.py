"""
Data Access Interfaces for Inventory Agent.
These interfaces define the contract between the agent and any data source.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class InventoryItem:
    """Represents an inventory item."""
    item_id: str
    item_name: str
    category: Optional[str] = None
    unit: Optional[str] = None
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    shelf_life_days: Optional[int] = None


@dataclass
class StockLevel:
    """Represents current stock level for an item at an outlet."""
    outlet_id: str
    item_id: str
    current_quantity: float
    reserved_quantity: float = 0.0
    damaged_quantity: float = 0.0
    expiry_quantity: float = 0.0
    last_updated: Optional[datetime] = None


@dataclass
class StockMovement:
    """Represents a stock movement transaction."""
    date: datetime
    outlet_id: str
    item_id: str
    quantity_received: float = 0.0
    quantity_used: float = 0.0
    quantity_wasted: float = 0.0
    quantity_adjusted: float = 0.0


@dataclass
class DemandHistory:
    """Represents historical demand/consumption data."""
    date: datetime
    outlet_id: str
    item_id: str
    quantity_consumed: float
    quantity_sold: Optional[float] = None


@dataclass
class SupplierInfo:
    """Represents supplier information."""
    supplier_id: str
    supplier_name: str
    minimum_order_quantity: Optional[float] = None
    lead_time_days: Optional[int] = None
    reorder_point: Optional[float] = None
    safety_stock: Optional[float] = None


class DataAccessInterface(ABC):
    """
    Abstract interface for data access.
    Any data source (CSV, JSON, database, API) must implement this interface.
    """
    
    @abstractmethod
    def get_inventory_items(self, outlet_id: Optional[str] = None) -> List[InventoryItem]:
        """Get all inventory items, optionally filtered by outlet."""
        pass
    
    @abstractmethod
    def get_inventory_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get a specific inventory item by ID."""
        pass
    
    @abstractmethod
    def get_stock_levels(self, outlet_id: Optional[str] = None, 
                         item_id: Optional[str] = None) -> List[StockLevel]:
        """Get current stock levels, optionally filtered."""
        pass
    
    @abstractmethod
    def get_stock_movements(self, outlet_id: Optional[str] = None,
                           item_id: Optional[str] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[StockMovement]:
        """Get stock movements within date range, optionally filtered."""
        pass
    
    @abstractmethod
    def get_demand_history(self, outlet_id: Optional[str] = None,
                          item_id: Optional[str] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[DemandHistory]:
        """Get demand/consumption history, optionally filtered."""
        pass
    
    @abstractmethod
    def get_supplier_info(self, supplier_id: Optional[str] = None) -> List[SupplierInfo]:
        """Get supplier information, optionally filtered by supplier ID."""
        pass
    
    @abstractmethod
    def get_outlets(self) -> List[str]:
        """Get list of all outlet IDs."""
        pass