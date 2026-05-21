# -*- coding: utf-8 -*-
"""
Product Model
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    selling_price = Column(Float, nullable=False, default=0)
    cost_price = Column(Float, nullable=False, default=0)
    quantity = Column(Float, nullable=False, default=0)
    unit = Column(String(50), nullable=False, default='kvm')
    barcode = Column(String(100), nullable=True, unique=True)
    eni = Column(Float, nullable=True)
    boyi = Column(Float, nullable=True)
    kvm = Column(Float, nullable=True)
    narx_per_kvm = Column(Float, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    area_sqm = Column(Float, nullable=True)
    product_type = Column(String(50), nullable=False, default='glass')
    note = Column(String(500), nullable=True)

    # Relationships
    category = relationship("Category", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")

    @property
    def profit_per_unit(self):
        """Profit per unit (auto-calculated)"""
        return self.selling_price - self.cost_price

    @property
    def is_remnant(self):
        """Check whether this row is a remnant glass piece."""
        return (self.product_type or "glass") == "remnant"

    def __repr__(self):
        return f"<Product {self.name}>"
