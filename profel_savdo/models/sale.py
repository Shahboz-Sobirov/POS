# -*- coding: utf-8 -*-
"""
Sale Models
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base


class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    total_amount = Column(Float, nullable=False)
    payment_type = Column(String(50), nullable=False)  # Naqd, Karta, Click, Qarz, Mixed
    payment_breakdown = Column(JSON, nullable=True)  # {"naqd": 100, "karta": 50, ...}
    profit = Column(Float, nullable=False, default=0)  # AUTO-CALCULATED
    sale_date = Column(DateTime, default=datetime.now)
    cashier = Column(String(100), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sale #{self.id} - {self.total_amount}>"


class SaleItem(Base):
    __tablename__ = 'sale_items'

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)  # Snapshot at sale time
    profit = Column(Float, nullable=False)  # AUTO-CALCULATED: (price - cost_price) * quantity

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")

    def __repr__(self):
        return f"<SaleItem {self.product_id} x{self.quantity}>"
