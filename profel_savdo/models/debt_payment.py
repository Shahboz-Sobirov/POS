# -*- coding: utf-8 -*-
"""
Debt Payment Model
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base


class DebtPayment(Base):
    __tablename__ = 'debt_payments'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_type = Column(String(50), nullable=False)  # Naqd, Karta, Click, Mixed
    payment_breakdown = Column(String(500), nullable=True)  # JSON string
    payment_date = Column(DateTime, default=datetime.now)
    note = Column(String(500), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="debt_payments")

    def __repr__(self):
        return f"<DebtPayment {self.amount} from Customer {self.customer_id}>"
