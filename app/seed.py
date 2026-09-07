from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from random import Random

from app.database import SessionLocal
from app.models import Franchise, Outlet, Sale, Product, Inventory, InventoryTransaction


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
