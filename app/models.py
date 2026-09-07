from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.orm import relationship

from app.database import Base


class Franchise(Base):
    __tablename__ = "franchises"

    franchise_id = Column(Integer, primary_key=True, index=True)
    franchise_name = Column(String(255), nullable=False)
    region = Column(String(100))
    owner_name = Column(String(255))

    outlets = relationship("Outlet", back_populates="franchise", lazy="selectin")


class Outlet(Base):
    __tablename__ = "outlets"

    outlet_id = Column(Integer, primary_key=True, index=True)
    franchise_id = Column(Integer, ForeignKey("franchises.franchise_id"), nullable=False)
    outlet_name = Column(String(255), nullable=False)
    location = Column(String(255))
    status = Column(String(50))

    franchise = relationship("Franchise", back_populates="outlets")
    sales = relationship("Sale", back_populates="outlet", lazy="selectin")


class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.outlet_id"), nullable=False)
    sale_date = Column(Date, nullable=False)
    revenue = Column(Numeric(12, 2))
    transaction_count = Column(Integer)

    outlet = relationship("Outlet", back_populates="sales")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100))
    unit = Column(String(50))
    unit_price = Column(Numeric(10, 2))

    inventory = relationship("Inventory", back_populates="product", lazy="selectin")


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.outlet_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    current_stock = Column(Numeric(10, 2), default=0)
    reorder_point = Column(Numeric(10, 2), default=0)
    reorder_quantity = Column(Numeric(10, 2), default=0)
    max_stock = Column(Numeric(10, 2))
    last_updated = Column(Date)

    outlet = relationship("Outlet")
    product = relationship("Product", back_populates="inventory")
    transactions = relationship("InventoryTransaction", back_populates="inventory", lazy="selectin")


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.inventory_id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(String(50))  # IN, OUT, WASTAGE, RETURN
    quantity = Column(Numeric(10, 2))
    reason = Column(String(255))

    inventory = relationship("Inventory", back_populates="transactions")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    order_id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.outlet_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    order_date = Column(Date)
    expected_delivery_date = Column(Date)
    quantity = Column(Numeric(10, 2))
    status = Column(String(50))  # PENDING, RECEIVED, CANCELLED

    outlet = relationship("Outlet")
    product = relationship("Product")
