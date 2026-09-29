from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from random import Random

from app.database import SessionLocal
from app.models import (
    Attendance,
    AuditComplianceRecord,
    AuditInspection,
    CampaignPerformance,
    Employee,
    Franchise,
    Inventory,
    InventoryTransaction,
    MarketingCampaign,
    Outlet,
    Product,
    Sale,
    Schedule,
)


def seed_data():
    db = SessionLocal()
    try:
        if db.query(Franchise).first():
            return

        burger_king = Franchise(franchise_name="Burger King North", region="North Region", owner_name="Alice Johnson")
        subway = Franchise(franchise_name="Subway South", region="South Region", owner_name="Bob Smith")
        db.add_all([burger_king, subway])
        db.commit()
        db.refresh(burger_king)
        db.refresh(subway)

        outlet1 = Outlet(franchise_id=burger_king.franchise_id, outlet_name="BK Downtown", location="Downtown", status="Active")
        outlet2 = Outlet(franchise_id=burger_king.franchise_id, outlet_name="BK Mall", location="Mall Road", status="Active")
        outlet3 = Outlet(franchise_id=subway.franchise_id, outlet_name="Subway City Center", location="City Center", status="Active")
        outlet4 = Outlet(franchise_id=subway.franchise_id, outlet_name="Subway Airport", location="Airport", status="Inactive")
        db.add_all([outlet1, outlet2, outlet3, outlet4])
        db.commit()
        db.refresh(outlet1)
        db.refresh(outlet2)
        db.refresh(outlet3)
        db.refresh(outlet4)

        _seed_outlet_sales(db, outlet1, 30, Decimal("1200"), Decimal("300"))
        _seed_outlet_sales(db, outlet2, 30, Decimal("900"), Decimal("250"))
        _seed_outlet_sales(db, outlet3, 30, Decimal("1500"), Decimal("400"))
        _seed_outlet_sales(db, outlet4, 30, Decimal("500"), Decimal("150"))

        _seed_inventory(db, [outlet1, outlet2, outlet3, outlet4])
        _seed_workforce(db, [outlet1, outlet2, outlet3, outlet4])
        _seed_marketing(db, [outlet1, outlet2, outlet3, outlet4])
        _seed_audit(db, [outlet1, outlet2, outlet3, outlet4])
    finally:
        db.close()


def _seed_outlet_sales(db, outlet, days, base_revenue, base_transactions):
    random = Random(outlet.outlet_id)
    today = date.today()

    for i in range(days):
        sale_date = today - timedelta(days=days - i - 1)
        revenue_multiplier = Decimal(str(0.7 + random.random() * 0.6))
        revenue = (base_revenue * revenue_multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        transaction_multiplier = Decimal(str(0.7 + random.random() * 0.6))
        transactions = int((base_transactions * transaction_multiplier).to_integral_value(rounding=ROUND_HALF_UP))

        sale = Sale(outlet_id=outlet.outlet_id, sale_date=sale_date, revenue=revenue, transaction_count=transactions)
        db.add(sale)

    db.commit()


def _seed_inventory(db, outlets):
    products = [
        Product(product_name="Burger Patties", category="Raw Material", unit="pieces", unit_price=Decimal("2.50")),
        Product(product_name="Burger Buns", category="Raw Material", unit="pieces", unit_price=Decimal("0.30")),
        Product(product_name="French Fries", category="Frozen", unit="kg", unit_price=Decimal("3.00")),
        Product(product_name="Soda Syrup", category="Beverage", unit="liter", unit_price=Decimal("4.00")),
        Product(product_name="Lettuce", category="Fresh", unit="kg", unit_price=Decimal("1.50")),
        Product(product_name="Sub Bread", category="Raw Material", unit="pieces", unit_price=Decimal("0.50")),
        Product(product_name="Cheese Slices", category="Dairy", unit="pieces", unit_price=Decimal("0.20")),
        Product(product_name="Tomato Sauce", category="Condiment", unit="liter", unit_price=Decimal("2.00")),
    ]
    db.add_all(products)
    db.commit()
    for product in products:
        db.refresh(product)

    today = date.today()
    random = Random(42)

    for outlet in outlets:
        for product in products:
            inventory = Inventory(
                outlet_id=outlet.outlet_id,
                product_id=product.product_id,
                current_stock=Decimal("0.00"),
                reorder_point=Decimal("0.00"),
                reorder_quantity=Decimal("0.00"),
                max_stock=None,
                last_updated=today,
            )
            db.add(inventory)
            db.commit()
            db.refresh(inventory)

            _seed_inventory_transactions(db, inventory, product, today, random)

    db.commit()


def _seed_inventory_transactions(db, inventory, product, today, random):
    days = 30
    base_daily_usage = Decimal(str(5 + random.randint(1, 15)))

    # Set thresholds based on average daily usage
    # reorder_point = 12 days supply
    # reorder_quantity = 14 days supply
    # max_stock = 50 days supply
    inventory.reorder_point = (base_daily_usage * Decimal("12")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    inventory.reorder_quantity = (base_daily_usage * Decimal("14")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    inventory.max_stock = (base_daily_usage * Decimal("50")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Generate daily OUT transactions for forecasting
    total_out = Decimal("0.00")
    daily_outs = []
    for i in range(days):
        usage_multiplier = Decimal(str(0.7 + random.random() * 0.6))
        out_quantity = (base_daily_usage * usage_multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        daily_outs.append(out_quantity)
        total_out += out_quantity

    total_wastage = Decimal("0.00")
    for i in range(days):
        transaction_date = today - timedelta(days=days - i - 1)
        _add_transaction(db, inventory, transaction_date, "OUT", daily_outs[i], "Daily usage")

        if random.random() < 0.15 and product.category in ("Fresh", "Dairy"):
            wastage = (base_daily_usage * Decimal(str(random.random() * 0.3))).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            if wastage > 0:
                _add_transaction(db, inventory, transaction_date, "WASTAGE", wastage, "Expired/damaged")
                total_wastage += wastage

    # Decide current stock level for demo realism
    profile_roll = random.random()
    if profile_roll < 0.10:
        # Critical: zero stock
        current_stock = Decimal("0.00")
    elif profile_roll < 0.30:
        # Low stock: 0.2x to 0.4x of 30-day usage
        current_stock = (total_out * Decimal(str(0.2 + random.random() * 0.2))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    elif profile_roll < 0.85:
        # Normal: 1.0x to 1.5x of 30-day usage
        current_stock = (total_out * Decimal(str(1.0 + random.random() * 0.5))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        # Overstock: 2.0x to 2.8x of 30-day usage
        current_stock = (total_out * Decimal(str(2.0 + random.random() * 0.8))).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    inventory.current_stock = current_stock

    # Set max_stock to trigger overstock only for high-stock items
    if profile_roll >= 0.85:
        inventory.max_stock = (total_out * Decimal("1.5")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        inventory.max_stock = (total_out * Decimal("3.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Initial IN = current + everything used/wasted
    initial_in = (current_stock + total_out + total_wastage).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    _add_transaction(db, inventory, today - timedelta(days=days), "IN", initial_in, "Initial stock")

    db.commit()


def _add_transaction(db, inventory, transaction_date, transaction_type, quantity, reason):
    transaction = InventoryTransaction(
        inventory_id=inventory.inventory_id,
        transaction_date=transaction_date,
        transaction_type=transaction_type,
        quantity=quantity,
        reason=reason,
    )
    db.add(transaction)
    db.commit()


def _seed_workforce(db, outlets):
    today = date.today()
    roles = ["Manager", "Cashier", "Chef", "Waiter", "Kitchen Staff", "Cleaner"]
    names = [
        ("Amit Sharma", "Manager"),
        ("Priya Patel", "Cashier"),
        ("Rahul Kumar", "Chef"),
        ("Sneha Gupta", "Waiter"),
        ("Vikram Singh", "Kitchen Staff"),
        ("Neha Verma", "Cashier"),
        ("Arjun Reddy", "Chef"),
        ("Divya Iyer", "Waiter"),
        ("Karan Mehta", "Cleaner"),
        ("Pooja Nair", "Manager"),
    ]

    random = Random(123)

    employees = []
    for outlet in outlets:
        # Skip inactive outlet partially
        staff_count = 3 if outlet.status == "Inactive" else 5 + random.randint(0, 3)
        for i in range(staff_count):
            name, role = names[(outlet.outlet_id + i) % len(names)]
            if outlet.status == "Inactive":
                emp_status = random.choice(["Inactive", "On Leave"])
            else:
                emp_status = random.choice(["Active", "Active", "Active", "On Leave"])

            employee = Employee(
                outlet_id=outlet.outlet_id,
                full_name=f"{name} ({outlet.outlet_name})",
                role=role if i > 0 else "Manager",
                email=f"employee{outlet.outlet_id}{i}@franchiseops.ai",
                phone=f"98765{outlet.outlet_id}{i:03d}",
                hourly_rate=Decimal(str(100 + random.randint(20, 150))),
                hire_date=today - timedelta(days=random.randint(30, 500)),
                status=emp_status,
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)
            employees.append(employee)

            _seed_attendance(db, employee, today, random)
            _seed_schedules(db, employee, today, random)

    db.commit()


def _seed_attendance(db, employee, today, random):
    statuses = ["PRESENT", "PRESENT", "PRESENT", "PRESENT", "PRESENT", "LATE", "ABSENT", "HALF_DAY"]
    for i in range(30):
        attendance_date = today - timedelta(days=29 - i)
        status = random.choice(statuses)
        if status == "PRESENT":
            hours = Decimal(str(7.5 + random.random() * 1.0))
        elif status == "LATE":
            hours = Decimal(str(6.0 + random.random() * 1.0))
        elif status == "HALF_DAY":
            hours = Decimal("4.00")
        else:
            hours = Decimal("0.00")

        attendance = Attendance(
            employee_id=employee.employee_id,
            attendance_date=attendance_date,
            status=status,
            hours_worked=hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            notes=None,
        )
        db.add(attendance)
    db.commit()


def _seed_schedules(db, employee, today, random):
    if employee.status != "Active":
        return

    for i in range(14):
        schedule_date = today - timedelta(days=7 - i)
        if schedule_date < today:
            schedule_status = random.choice(["COMPLETED", "COMPLETED", "CANCELLED"])
        else:
            schedule_status = "SCHEDULED"

        start_hour = 8 + random.randint(0, 4)
        shift_hours = 6 + random.randint(0, 4)
        shift_start = f"{start_hour:02d}:00"
        shift_end = f"{(start_hour + shift_hours) % 24:02d}:00"

        schedule = Schedule(
            employee_id=employee.employee_id,
            schedule_date=schedule_date,
            shift_start=shift_start,
            shift_end=shift_end,
            status=schedule_status,
        )
        db.add(schedule)
    db.commit()


def _seed_marketing(db, outlets):
    today = date.today()
    random = Random(456)

    campaign_templates = [
        ("Summer Burger Bonanza", "Discount", 5000),
        ("Social Media Blast", "Social Media", 3000),
        ("Weekend Family Combo", "Discount", 7000),
        ("Email Newsletter Promo", "Email", 1500),
        ("Festival Special", "Discount", 8000),
        ("Local Billboard", "Billboard", 4000),
        ("Loyalty Program", "Email", 2000),
        ("New Menu Launch", "Social Media", 6000),
    ]

    for outlet in outlets:
        # Inactive outlet gets fewer/older campaigns
        num_campaigns = 1 if outlet.status == "Inactive" else random.randint(2, 4)
        for i in range(num_campaigns):
            template = campaign_templates[(outlet.outlet_id + i) % len(campaign_templates)]
            start_offset = random.randint(-20, -5)
            duration = random.randint(7, 21)
            start_date = today + timedelta(days=start_offset)
            end_date = start_date + timedelta(days=duration)
            status = "Completed" if end_date < today else random.choice(["Active", "Completed", "Planned"])

            campaign = MarketingCampaign(
                outlet_id=outlet.outlet_id,
                campaign_name=f"{template[0]} - {outlet.outlet_name}",
                campaign_type=template[1],
                start_date=start_date,
                end_date=end_date,
                budget=Decimal(str(template[2])),
                status=status,
            )
            db.add(campaign)
            db.commit()
            db.refresh(campaign)

            _seed_campaign_performance(db, campaign, start_date, end_date, template[1], random)

    db.commit()


def _seed_campaign_performance(db, campaign, start_date, end_date, campaign_type, random):
    days = max(1, (end_date - start_date).days + 1)
    total_budget = float(campaign.budget)

    for i in range(days):
        performance_date = start_date + timedelta(days=i)

        # Different campaign types have different engagement patterns
        if campaign_type == "Social Media":
            base_impressions = random.randint(2000, 5000)
            ctr = 0.03 + random.random() * 0.04
        elif campaign_type == "Email":
            base_impressions = random.randint(500, 1500)
            ctr = 0.05 + random.random() * 0.10
        elif campaign_type == "Discount":
            base_impressions = random.randint(1000, 3000)
            ctr = 0.02 + random.random() * 0.05
        else:  # Billboard
            base_impressions = random.randint(3000, 8000)
            ctr = 0.005 + random.random() * 0.015

        impressions = base_impressions
        clicks = int(impressions * ctr)
        conversions = int(clicks * (0.05 + random.random() * 0.15))
        engagement_score = Decimal(str(min(100, ctr * 100 * 5 + random.random() * 20)))
        revenue = Decimal(str(total_budget * 0.2 * (0.8 + random.random() * 0.6)))

        performance = CampaignPerformance(
            campaign_id=campaign.campaign_id,
            performance_date=performance_date,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            engagement_score=engagement_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            revenue=revenue.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        )
        db.add(performance)
    db.commit()


def _seed_audit(db, outlets):
    today = date.today()
    random = Random(789)

    # Compliance snapshots (two per outlet) for intelligence pipeline
    compliance_profiles = {
        1: (92.0, 96.5, 1, 0),
        2: (58.0, 64.0, 4, 2),
        3: (83.0, 76.5, 2, 1),
        4: (89.0, 81.0, 1, 2),
    }

    inspections = [
        (1, "Health Inspector Alvarez", Decimal("96.5"), "Passed", 0, 1, "Impeccable cleanliness."),
        (2, "Regional Auditor Novak", Decimal("64.0"), "Failed", 2, 4, "Refrigeration gasket damaged."),
        (3, "Health Inspector Alvarez", Decimal("76.5"), "Warning", 1, 3, "Handwashing sink temp below standard."),
        (4, "Corporate Compliance Lead Chen", Decimal("88.0"), "Passed", 0, 2, "Sanitization station restocked on site."),
    ]

    for outlet in outlets:
        prof = compliance_profiles.get(outlet.outlet_id, (80.0, 78.0, 2, 1))
        for offset, score, violations in (
            (45, prof[0], prof[2]),
            (15, prof[1], prof[3]),
        ):
            db.add(
                AuditComplianceRecord(
                    outlet_id=outlet.outlet_id,
                    record_date=today - timedelta(days=offset),
                    compliance_score=Decimal(str(score)),
                    violation_count=violations,
                )
            )

    for outlet_id, auditor, score, status, critical, minor, notes in inspections:
        db.add(
            AuditInspection(
                outlet_id=outlet_id,
                inspection_date=today - timedelta(days=random.randint(5, 25)),
                auditor_name=auditor,
                score=score,
                status=status,
                critical_violations=critical,
                minor_violations=minor,
                notes=notes,
            )
        )

    db.commit()
