"""
CSV-based data provider implementation.
This is the standalone data source for development and testing.
"""

import csv
import os
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
import random

from .interfaces import (
    DataAccessInterface, InventoryItem, StockLevel, StockMovement,
    DemandHistory, SupplierInfo
)
from ..config.settings import settings


class CSVDataProvider(DataAccessInterface):
    """
    CSV-based implementation of the data access interface.
    Creates sample data if files don't exist.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or settings.DATA_DIR
        os.makedirs(self.data_dir, exist_ok=True)
        self._ensure_sample_data()
    
    def _ensure_sample_data(self):
        """Create sample data files if they don't exist."""
        if not os.path.exists(settings.INVENTORY_FILE):
            self._create_sample_inventory()
        if not os.path.exists(settings.MOVEMENTS_FILE):
            self._create_sample_movements()
        if not os.path.exists(settings.DEMAND_FILE):
            self._create_sample_demand()
        if not os.path.exists(settings.SUPPLIERS_FILE):
            self._create_sample_suppliers()
        if not os.path.exists(settings.OUTLETS_FILE):
            self._create_sample_outlets()
    
    def _create_sample_inventory(self):
        """Create sample inventory data."""
        inventory_items = [
            {"item_id": "ITEM001", "item_name": "Milk", "category": "Dairy", "unit": "litres", "supplier_id": "SUP001", "unit_cost": 60},
            {"item_id": "ITEM002", "item_name": "Bread", "category": "Bakery", "unit": "loaves", "supplier_id": "SUP002", "unit_cost": 40},
            {"item_id": "ITEM003", "item_name": "Eggs", "category": "Dairy", "unit": "pieces", "supplier_id": "SUP001", "unit_cost": 8},
            {"item_id": "ITEM004", "item_name": "Butter", "category": "Dairy", "unit": "kg", "supplier_id": "SUP001", "unit_cost": 450},
            {"item_id": "ITEM005", "item_name": "Sugar", "category": "Grocery", "unit": "kg", "supplier_id": "SUP003", "unit_cost": 45},
            {"item_id": "ITEM006", "item_name": "Flour", "category": "Grocery", "unit": "kg", "supplier_id": "SUP003", "unit_cost": 35},
            {"item_id": "ITEM007", "item_name": "Cooking Oil", "category": "Grocery", "unit": "litres", "supplier_id": "SUP004", "unit_cost": 180},
            {"item_id": "ITEM008", "item_name": "Tomatoes", "category": "Vegetables", "unit": "kg", "supplier_id": "SUP005", "unit_cost": 60},
        ]
        
        outlets = ["OUT101", "OUT102", "OUT103", "OUT104", "OUT105"]
        
        with open(settings.INVENTORY_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['item_id', 'item_name', 'category', 'unit', 'supplier_id', 'unit_cost'])
            for item in inventory_items:
                writer.writerow([
                    item['item_id'], item['item_name'], item['category'],
                    item['unit'], item['supplier_id'], item['unit_cost']
                ])
    
    def _create_sample_suppliers(self):
        """Create sample supplier data."""
        suppliers = [
            {"supplier_id": "SUP001", "supplier_name": "Dairy Fresh Co.", "minimum_order_quantity": 50, "lead_time_days": 2, "safety_stock": 20},
            {"supplier_id": "SUP002", "supplier_name": "Bakery Supplies Ltd.", "minimum_order_quantity": 30, "lead_time_days": 1, "safety_stock": 10},
            {"supplier_id": "SUP003", "supplier_name": "Grocery Wholesalers", "minimum_order_quantity": 25, "lead_time_days": 3, "safety_stock": 15},
            {"supplier_id": "SUP004", "supplier_name": "Oil & Spices Corp.", "minimum_order_quantity": 20, "lead_time_days": 4, "safety_stock": 10},
            {"supplier_id": "SUP005", "supplier_name": "Fresh Produce Inc.", "minimum_order_quantity": 10, "lead_time_days": 1, "safety_stock": 5},
        ]
        
        with open(settings.SUPPLIERS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['supplier_id', 'supplier_name', 'minimum_order_quantity', 'lead_time_days', 'safety_stock'])
            for sup in suppliers:
                writer.writerow([
                    sup['supplier_id'], sup['supplier_name'],
                    sup['minimum_order_quantity'], sup['lead_time_days'],
                    sup['safety_stock']
                ])
    
    def _create_sample_outlets(self):
        """Create sample outlet data."""
        outlets = [
            {"outlet_id": "OUT101", "outlet_name": "Downtown Store", "location": "Main Street"},
            {"outlet_id": "OUT102", "outlet_name": "Uptown Store", "location": "Park Avenue"},
            {"outlet_id": "OUT103", "outlet_name": "Mall Store", "location": "City Mall"},
            {"outlet_id": "OUT104", "outlet_name": "Suburb Store", "location": "Green Valley"},
            {"outlet_id": "OUT105", "outlet_name": "Highway Store", "location": "Expressway"},
        ]
        
        with open(settings.OUTLETS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['outlet_id', 'outlet_name', 'location'])
            for outlet in outlets:
                writer.writerow([outlet['outlet_id'], outlet['outlet_name'], outlet['location']])
    
    def _create_sample_movements(self):
        """Create sample stock movement data."""
        outlets = ["OUT101", "OUT102", "OUT103", "OUT104", "OUT105"]
        items = ["ITEM001", "ITEM002", "ITEM003", "ITEM004", "ITEM005", "ITEM006", "ITEM007", "ITEM008"]
        
        with open(settings.MOVEMENTS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'outlet_id', 'item_id', 'quantity_received', 'quantity_used', 'quantity_wasted', 'quantity_adjusted'])
            
            # Generate 60 days of data
            for day in range(60, 0, -1):
                date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
                for outlet in outlets:
                    for item in items:
                        base_consumption = random.randint(5, 30)
                        waste = random.randint(0, 3)
                        received = base_consumption + random.randint(0, 5) if day % 7 == 0 else 0
                        writer.writerow([
                            date, outlet, item,
                            received, base_consumption, waste, 0
                        ])
    
    def _create_sample_demand(self):
        """Create sample demand data."""
        outlets = ["OUT101", "OUT102", "OUT103", "OUT104", "OUT105"]
        items = ["ITEM001", "ITEM002", "ITEM003", "ITEM004", "ITEM005", "ITEM006", "ITEM007", "ITEM008"]
        
        with open(settings.DEMAND_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'outlet_id', 'item_id', 'quantity_consumed', 'quantity_sold'])
            
            for day in range(60, 0, -1):
                date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
                for outlet in outlets:
                    for item in items:
                        consumed = random.randint(5, 30)
                        sold = consumed - random.randint(0, 3)
                        writer.writerow([date, outlet, item, consumed, sold])
    
    def _load_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Load CSV file into list of dictionaries."""
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def get_inventory_items(self, outlet_id: Optional[str] = None) -> List[InventoryItem]:
        """Get inventory items."""
        data = self._load_csv(settings.INVENTORY_FILE)
        items = []
        for row in data:
            items.append(InventoryItem(
                item_id=row['item_id'],
                item_name=row['item_name'],
                category=row.get('category'),
                unit=row.get('unit'),
                supplier_id=row.get('supplier_id'),
                supplier_name=None,  # Will be resolved later
                unit_cost=Decimal(row['unit_cost']) if row.get('unit_cost') else None,
                shelf_life_days=int(row['shelf_life_days']) if row.get('shelf_life_days') else None
            ))
        return items
    
    def get_inventory_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get a specific inventory item."""
        items = self.get_inventory_items()
        for item in items:
            if item.item_id == item_id:
                return item
        return None
    
    def get_stock_levels(self, outlet_id: Optional[str] = None,
                        item_id: Optional[str] = None) -> List[StockLevel]:
        """Get current stock levels from movements data."""
        movements = self._load_csv(settings.MOVEMENTS_FILE)
        
        # Calculate current stock from movements
        stock_map = {}
        for row in movements:
            oid = row['outlet_id']
            iid = row['item_id']
            key = f"{oid}_{iid}"
            
            if key not in stock_map:
                stock_map[key] = {
                    'outlet_id': oid,
                    'item_id': iid,
                    'current_quantity': 0.0,
                    'reserved_quantity': 0.0,
                    'damaged_quantity': 0.0,
                    'expiry_quantity': 0.0,
                    'last_updated': datetime.now()
                }
            
            stock_map[key]['current_quantity'] += float(row.get('quantity_received', 0))
            stock_map[key]['current_quantity'] -= float(row.get('quantity_used', 0))
            stock_map[key]['current_quantity'] -= float(row.get('quantity_wasted', 0))
        
        # Filter results
        results = []
        for key, data in stock_map.items():
            if outlet_id and data['outlet_id'] != outlet_id:
                continue
            if item_id and data['item_id'] != item_id:
                continue
            
            # Add some random variation for demo purposes
            data['current_quantity'] += random.randint(-5, 10)
            if data['current_quantity'] < 0:
                data['current_quantity'] = random.randint(10, 50)
            
            results.append(StockLevel(
                outlet_id=data['outlet_id'],
                item_id=data['item_id'],
                current_quantity=max(0, data['current_quantity']),
                reserved_quantity=data['reserved_quantity'],
                damaged_quantity=data['damaged_quantity'],
                expiry_quantity=data['expiry_quantity'],
                last_updated=data['last_updated']
            ))
        
        return results
    
    def get_stock_movements(self, outlet_id: Optional[str] = None,
                           item_id: Optional[str] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[StockMovement]:
        """Get stock movements."""
        data = self._load_csv(settings.MOVEMENTS_FILE)
        
        movements = []
        for row in data:
            date = datetime.strptime(row['date'], '%Y-%m-%d')
            
            if start_date and date < start_date:
                continue
            if end_date and date > end_date:
                continue
            if outlet_id and row['outlet_id'] != outlet_id:
                continue
            if item_id and row['item_id'] != item_id:
                continue
            
            movements.append(StockMovement(
                date=date,
                outlet_id=row['outlet_id'],
                item_id=row['item_id'],
                quantity_received=float(row.get('quantity_received', 0)),
                quantity_used=float(row.get('quantity_used', 0)),
                quantity_wasted=float(row.get('quantity_wasted', 0)),
                quantity_adjusted=float(row.get('quantity_adjusted', 0))
            ))
        
        return movements
    
    def get_demand_history(self, outlet_id: Optional[str] = None,
                          item_id: Optional[str] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[DemandHistory]:
        """Get demand history."""
        data = self._load_csv(settings.DEMAND_FILE)
        
        history = []
        for row in data:
            date = datetime.strptime(row['date'], '%Y-%m-%d')
            
            if start_date and date < start_date:
                continue
            if end_date and date > end_date:
                continue
            if outlet_id and row['outlet_id'] != outlet_id:
                continue
            if item_id and row['item_id'] != item_id:
                continue
            
            history.append(DemandHistory(
                date=date,
                outlet_id=row['outlet_id'],
                item_id=row['item_id'],
                quantity_consumed=float(row.get('quantity_consumed', 0)),
                quantity_sold=float(row.get('quantity_sold', 0)) if row.get('quantity_sold') else None
            ))
        
        return history
    
    def get_supplier_info(self, supplier_id: Optional[str] = None) -> List[SupplierInfo]:
        """Get supplier information."""
        data = self._load_csv(settings.SUPPLIERS_FILE)
        
        suppliers = []
        for row in data:
            if supplier_id and row['supplier_id'] != supplier_id:
                continue
            
            suppliers.append(SupplierInfo(
                supplier_id=row['supplier_id'],
                supplier_name=row['supplier_name'],
                minimum_order_quantity=float(row['minimum_order_quantity']) if row.get('minimum_order_quantity') else None,
                lead_time_days=int(row['lead_time_days']) if row.get('lead_time_days') else None,
                reorder_point=float(row.get('reorder_point')) if row.get('reorder_point') else None,
                safety_stock=float(row.get('safety_stock')) if row.get('safety_stock') else None
            ))
        
        return suppliers
    
    def get_outlets(self) -> List[str]:
        """Get list of outlets."""
        data = self._load_csv(settings.OUTLETS_FILE)
        return [row['outlet_id'] for row in data]