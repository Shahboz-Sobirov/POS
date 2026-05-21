# -*- coding: utf-8 -*-
"""
Category Service
"""
from models.base import Session
from models.category import Category
from models.product import Product


class CategoryService:
    """Category business logic"""

    @staticmethod
    def get_all():
        """Get all categories"""
        session = Session()
        try:
            categories = session.query(Category).order_by(Category.name).all()
            session.expunge_all()
            return categories
        except Exception as e:
            print(f"[ERROR] CategoryService.get_all: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_by_id(category_id):
        """Get category by ID"""
        session = Session()
        try:
            category = session.query(Category).filter_by(id=category_id).first()
            if category:
                session.expunge(category)
            return category
        except Exception as e:
            print(f"[ERROR] CategoryService.get_by_id: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def create(name, color="#3498db", icon=""):
        """Create new category"""
        if not name or not name.strip():
            raise ValueError("Kategoriya nomi bo'sh bo'lishi mumkin emas")

        session = Session()
        try:
            category = Category(
                name=name.strip(),
                color=color,
                icon=icon or None,
            )
            session.add(category)
            session.commit()

            print(f"[OK] Category created: ID={category.id}, Name={category.name}")

            session.refresh(category)
            session.expunge(category)
            return category
        except Exception as e:
            session.rollback()
            print(f"[ERROR] CategoryService.create: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def update(category_id, name=None, color=None, icon=None):
        """Update category"""
        session = Session()
        try:
            category = session.query(Category).filter_by(id=category_id).first()
            if not category:
                raise ValueError("Kategoriya topilmadi")

            if name is not None:
                if not name.strip():
                    raise ValueError("Kategoriya nomi bo'sh bo'lishi mumkin emas")
                category.name = name.strip()
            if color is not None:
                category.color = color
            if icon is not None:
                category.icon = icon or None

            session.commit()

            print(f"[OK] Category updated: ID={category.id}")

            session.refresh(category)
            session.expunge(category)
            return category
        except Exception as e:
            session.rollback()
            print(f"[ERROR] CategoryService.update: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def delete(category_id):
        """Delete category"""
        session = Session()
        try:
            category = session.query(Category).filter_by(id=category_id).first()
            if not category:
                raise ValueError("Kategoriya topilmadi")

            products_count = session.query(Product).filter_by(category_id=category_id).count()
            if products_count > 0:
                raise ValueError(
                    "Bu kategoriyada mahsulotlar bor. Avval mahsulotlarni boshqa kategoriyaga o'tkazing yoki o'chiring"
                )

            session.delete(category)
            session.commit()

            print(f"[OK] Category deleted: ID={category_id}")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] CategoryService.delete: {e}")
            raise e
        finally:
            Session.remove()
