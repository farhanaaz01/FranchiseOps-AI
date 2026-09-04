from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from random import Random

from app.database import SessionLocal
from app.models import Franchise, Outlet, Sale


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
