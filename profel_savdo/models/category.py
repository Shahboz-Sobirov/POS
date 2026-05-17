# -*- coding: utf-8 -*-
"""
Category Model
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(20), nullable=True, default='#3498db')
    icon = Column(String(10), nullable=True, default='📦')

    # Relationships
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category {self.name}>"
