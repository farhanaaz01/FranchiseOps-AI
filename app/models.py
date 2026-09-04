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
