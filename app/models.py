from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Date, Numeric, Text
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


# ------------------- Milestone 3: Workforce & Marketing -------------------

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.outlet_id"), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(100))  # Manager, Cashier, Chef, Waiter, etc.
    email = Column(String(255))
    phone = Column(String(50))
    hourly_rate = Column(Numeric(10, 2))
    hire_date = Column(Date)
    status = Column(String(50))  # Active, Inactive, On Leave

    outlet = relationship("Outlet")
    attendances = relationship("Attendance", back_populates="employee", lazy="selectin")
    schedules = relationship("Schedule", back_populates="employee", lazy="selectin")


class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    attendance_date = Column(Date, nullable=False)
    status = Column(String(50))  # PRESENT, ABSENT, LATE, HALF_DAY
    hours_worked = Column(Numeric(5, 2))
    notes = Column(String(255))

    employee = relationship("Employee", back_populates="attendances")


class Schedule(Base):
    __tablename__ = "schedules"

    schedule_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False)
    schedule_date = Column(Date, nullable=False)
    shift_start = Column(String(10))  # HH:MM
    shift_end = Column(String(10))    # HH:MM
    status = Column(String(50))  # SCHEDULED, COMPLETED, CANCELLED

    employee = relationship("Employee", back_populates="schedules")


class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    campaign_id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.outlet_id"), nullable=False)
    campaign_name = Column(String(255), nullable=False)
    campaign_type = Column(String(100))  # Social Media, Email, Discount, Billboard
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(Numeric(12, 2))
    status = Column(String(50))  # Active, Completed, Cancelled, Planned

    outlet = relationship("Outlet")
    performances = relationship("CampaignPerformance", back_populates="campaign", lazy="selectin")


class CampaignPerformance(Base):
    __tablename__ = "campaign_performance"

    performance_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("marketing_campaigns.campaign_id"), nullable=False)
    performance_date = Column(Date, nullable=False)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    engagement_score = Column(Numeric(5, 2))  # 0-100
    revenue = Column(Numeric(12, 2), default=0)

    campaign = relationship("MarketingCampaign", back_populates="performances")


# ------------------- Milestone 4: Audit, Intelligence, Notifications -------------------


class AuditComplianceRecord(Base):
    """Time-series compliance snapshots feeding the intelligence pipeline."""

    __tablename__ = "audit_compliance_records"

    record_id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.outlet_id"), nullable=False)
    record_date = Column(Date, nullable=False)
    compliance_score = Column(Numeric(5, 2), nullable=False)
    violation_count = Column(Integer, default=0)

    outlet = relationship("Outlet")


class AuditInspection(Base):
    """Manual health / compliance inspections (Audit Agent CRUD)."""

    __tablename__ = "audit_inspections"

    audit_id = Column(Integer, primary_key=True, index=True)
    outlet_id = Column(Integer, ForeignKey("outlets.outlet_id"), nullable=False)
    inspection_date = Column(Date, nullable=False)
    auditor_name = Column(String(255), nullable=False)
    score = Column(Numeric(5, 2), nullable=False)
    status = Column(String(50), nullable=False)  # Passed, Warning, Failed
    critical_violations = Column(Integer, default=0)
    minor_violations = Column(Integer, default=0)
    notes = Column(String(1000))

    outlet = relationship("Outlet")


class IntelligencePipelineRun(Base):
    """Persisted Franchise Intelligence Engine runs."""

    __tablename__ = "intelligence_pipeline_runs"

    run_id = Column(Integer, primary_key=True, index=True)
    generated_at = Column(DateTime, nullable=False)
    outlet_count = Column(Integer, nullable=False)
    output_json = Column(Text, nullable=False)
    is_latest = Column(Boolean, default=True)


class Notification(Base):
    """Unified alerts and workflow triggers across agents."""

    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    alert_key = Column(String(120), unique=True, index=True)
    domain = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    outlet_id = Column(Integer, ForeignKey("outlets.outlet_id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    status = Column(String(50), default="active")
    source_agent = Column(String(100))
    affected_area = Column(String(255))
    metric = Column(String(100))
    metric_value = Column(Numeric(12, 4))
    threshold_value = Column(Numeric(12, 4))
    recommendation = Column(String(1000))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    outlet = relationship("Outlet")
    action_plans = relationship("ActionPlan", back_populates="notification", lazy="selectin")


class ActionPlan(Base):
    """Recommended remediation steps linked to notifications."""

    __tablename__ = "action_plans"

    plan_id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.notification_id"), nullable=True)
    outlet_id = Column(Integer, ForeignKey("outlets.outlet_id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(2000))
    priority = Column(String(20), default="medium")
    status = Column(String(50), default="open")
    due_date = Column(Date)
    created_at = Column(DateTime, nullable=False)

    notification = relationship("Notification", back_populates="action_plans")
    outlet = relationship("Outlet")
