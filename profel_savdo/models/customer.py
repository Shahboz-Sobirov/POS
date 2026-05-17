# -*- coding: utf-8 -*-
"""
Customer Model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(50), nullable=True)
    total_debt = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    sales = relationship("Sale", back_populates="customer")
    debt_payments = relationship("DebtPayment", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.full_name}>"
