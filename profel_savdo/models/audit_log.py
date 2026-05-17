# -*- coding: utf-8 -*-
"""
Audit Log Model - Anti-Fraud Security
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from models.base import Base


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    action = Column(String(100), nullable=False)  # sale_created, product_edited, debt_paid, etc.
    user = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)  # sale, product, customer, etc.
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # JSON string with details
    timestamp = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user}>"
