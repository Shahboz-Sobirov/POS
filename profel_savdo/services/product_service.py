# -*- coding: utf-8 -*-
"""
Product Service
"""
from sqlalchemy.orm import joinedload
from models.base import Session
from models.product import Product
from models.category import Category


class ProductService:
    """Product business logic"""

    @staticmethod
    def get_all():
        """Get all products with eager-loaded category"""
        session = Session()
        try:
            products = session.query(Product).options(
                joinedload(Product.category)
            ).order_by(Product.name).all()
            # Make objects independent from session
            session.expunge_all()
            return products
        except Exception as e:
            print(f"[ERROR] ProductService.get_all: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_by_id(product_id):
        """Get product by ID with eager-loaded category"""
        session = Session()
        try:
            product = session.query(Product).options(
                joinedload(Product.category)
            ).filter_by(id=product_id).first()
            if product:
                session.expunge(product)
            return product
        except Exception as e:
            print(f"[ERROR] ProductService.get_by_id: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_by_category(category_id):
        """Get products by category with eager-loaded category"""
        session = Session()
        try:
            products = session.query(Product).options(
                joinedload(Product.category)
            ).filter_by(category_id=category_id).order_by(Product.name).all()
            session.expunge_all()
            return products
        except Exception as e:
            print(f"[ERROR] ProductService.get_by_category: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def search(query):
        """Search products by name with eager-loaded category"""
        session = Session()
        try:
            products = session.query(Product).options(
                joinedload(Product.category)
            ).filter(
                Product.name.ilike(f'%{query}%')
            ).order_by(Product.name).all()
            session.expunge_all()
            return products
        except Exception as e:
            print(f"[ERROR] ProductService.search: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def create(name, category_id, selling_price, cost_price, quantity, unit, barcode=None):
        """Create new product"""
        # Validation
        if not name or not name.strip():
            raise ValueError("Mahsulot nomi bo'sh bo'lishi mumkin emas")

        if selling_price <= 0:
            raise ValueError("Sotuv narxi 0 dan katta bo'lishi kerak")

        if cost_price < 0:
            raise ValueError("Kelgan narx manfiy bo'lishi mumkin emas")

        if quantity < 0:
            raise ValueError("Ombor soni manfiy bo'lishi mumkin emas")

        if not unit or not unit.strip():
            raise ValueError("Birlik bo'sh bo'lishi mumkin emas")

        session = Session()
        try:
            product = Product(
                name=name.strip(),
                category_id=category_id,
                selling_price=selling_price,
                cost_price=cost_price,
                quantity=quantity,
                unit=unit.strip(),
                barcode=barcode
            )
            session.add(product)
            session.commit()

            print(f"[OK] Product created: ID={product.id}, Name={product.name}")

            # Eager load category before detaching
            session.refresh(product)
            _ = product.category  # Force load
            session.expunge(product)

            return product
        except Exception as e:
            session.rollback()
            print(f"[ERROR] ProductService.create: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def update(product_id, **kwargs):
        """Update product"""
        session = Session()
        try:
            product = session.query(Product).options(
                joinedload(Product.category)
            ).filter_by(id=product_id).first()

            if not product:
                raise ValueError("Mahsulot topilmadi")

            # Validation
            if 'name' in kwargs and kwargs['name'] is not None:
                if not kwargs['name'].strip():
                    raise ValueError("Mahsulot nomi bo'sh bo'lishi mumkin emas")
                kwargs['name'] = kwargs['name'].strip()

            if 'selling_price' in kwargs and kwargs['selling_price'] is not None:
                if kwargs['selling_price'] <= 0:
                    raise ValueError("Sotuv narxi 0 dan katta bo'lishi kerak")

            if 'cost_price' in kwargs and kwargs['cost_price'] is not None:
                if kwargs['cost_price'] < 0:
                    raise ValueError("Kelgan narx manfiy bo'lishi mumkin emas")

            if 'quantity' in kwargs and kwargs['quantity'] is not None:
                if kwargs['quantity'] < 0:
                    raise ValueError("Ombor soni manfiy bo'lishi mumkin emas")

            if 'unit' in kwargs and kwargs['unit'] is not None:
                if not kwargs['unit'].strip():
                    raise ValueError("Birlik bo'sh bo'lishi mumkin emas")
                kwargs['unit'] = kwargs['unit'].strip()

            for key, value in kwargs.items():
                if hasattr(product, key) and value is not None:
                    setattr(product, key, value)

            session.commit()

            print(f"[OK] Product updated: ID={product.id}")

            session.refresh(product)
            _ = product.category  # Force load
            session.expunge(product)

            return product
        except Exception as e:
            session.rollback()
            print(f"[ERROR] ProductService.update: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def delete(product_id):
        """Delete product"""
        session = Session()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                raise ValueError("Mahsulot topilmadi")

            session.delete(product)
            session.commit()

            print(f"[OK] Product deleted: ID={product_id}")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] ProductService.delete: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def update_stock(product_id, quantity_change):
        """Update product stock"""
        session = Session()
        try:
            product = session.query(Product).options(
                joinedload(Product.category)
            ).filter_by(id=product_id).first()

            if not product:
                raise ValueError("Mahsulot topilmadi")

            product.quantity += quantity_change
            session.commit()

            print(f"[OK] Stock updated: ID={product_id}, Change={quantity_change}")

            session.refresh(product)
            _ = product.category  # Force load
            session.expunge(product)

            return product
        except Exception as e:
            session.rollback()
            print(f"[ERROR] ProductService.update_stock: {e}")
            raise e
        finally:
            Session.remove()
