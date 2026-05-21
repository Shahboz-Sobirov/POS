# -*- coding: utf-8 -*-
"""
Product Service
"""
from sqlalchemy.orm import joinedload

from models.base import Session
from models.product import Product
from utils.formatter import calculate_area_sqm, parse_decimal


class ProductService:
    """Product business logic"""

    @staticmethod
    def get_all():
        """Get all products with eager-loaded category."""
        session = Session()
        try:
            products = session.query(Product).options(
                joinedload(Product.category)
            ).order_by(Product.product_type.asc(), Product.name.asc()).all()
            session.expunge_all()
            return products
        except Exception as e:
            print(f"[ERROR] ProductService.get_all: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_regular_products():
        """Get regular glass products."""
        session = Session()
        try:
            products = session.query(Product).options(
                joinedload(Product.category)
            ).filter(
                Product.product_type != 'remnant'
            ).order_by(Product.name.asc()).all()
            session.expunge_all()
            return products
        except Exception as e:
            print(f"[ERROR] ProductService.get_regular_products: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_remnants():
        """Get remnant glass items."""
        session = Session()
        try:
            products = session.query(Product).options(
                joinedload(Product.category)
            ).filter_by(
                product_type='remnant'
            ).order_by(Product.name.asc()).all()
            session.expunge_all()
            return products
        except Exception as e:
            print(f"[ERROR] ProductService.get_remnants: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_by_id(product_id):
        """Get product by ID with eager-loaded category."""
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
        """Get products by category with eager-loaded category."""
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
        """Search products by name with eager-loaded category."""
        session = Session()
        try:
            products = session.query(Product).options(
                joinedload(Product.category)
            ).filter(
                Product.name.ilike(f'%{query}%')
            ).order_by(Product.product_type.asc(), Product.name.asc()).all()
            session.expunge_all()
            return products
        except Exception as e:
            print(f"[ERROR] ProductService.search: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def create(
        name,
        category_id,
        selling_price,
        cost_price,
        quantity,
        unit='kvm',
        barcode=None,
        eni=None,
        boyi=None,
        kvm=None,
        narx_per_kvm=None,
        width=None,
        height=None,
        area_sqm=None,
        product_type='glass',
        note=None,
    ):
        """Create new product."""
        payload = ProductService._validate_product_data(
            name=name,
            selling_price=narx_per_kvm if narx_per_kvm is not None else selling_price,
            cost_price=cost_price,
            quantity=quantity,
            unit=unit,
            width=eni if eni is not None else width,
            height=boyi if boyi is not None else height,
            area_sqm=kvm if kvm is not None else area_sqm,
            product_type=product_type,
            note=note,
        )

        session = Session()
        try:
            product = Product(
                name=payload['name'],
                category_id=category_id,
                selling_price=payload['selling_price'],
                cost_price=payload['cost_price'],
                quantity=payload['quantity'],
                unit=payload['unit'],
                barcode=barcode,
                eni=payload['eni'],
                boyi=payload['boyi'],
                kvm=payload['kvm'],
                narx_per_kvm=payload['narx_per_kvm'],
                width=payload['width'],
                height=payload['height'],
                area_sqm=payload['area_sqm'],
                product_type=payload['product_type'],
                note=payload['note'],
            )
            session.add(product)
            session.commit()

            print(f"[OK] Product created: ID={product.id}, Name={product.name}")

            session.refresh(product)
            _ = product.category
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
        """Update product."""
        session = Session()
        try:
            product = session.query(Product).options(
                joinedload(Product.category)
            ).filter_by(id=product_id).first()

            if not product:
                raise ValueError("Oyna topilmadi")

            payload = ProductService._validate_product_data(
                name=kwargs.get('name', product.name),
                selling_price=kwargs.get(
                    'narx_per_kvm',
                    kwargs.get('selling_price', product.selling_price)
                ),
                cost_price=kwargs.get('cost_price', product.cost_price),
                quantity=kwargs.get('quantity', product.quantity),
                unit=kwargs.get('unit', product.unit),
                width=kwargs.get('eni', kwargs.get('width', product.eni or product.width)),
                height=kwargs.get('boyi', kwargs.get('height', product.boyi or product.height)),
                # glass uchun area_sqm = bitta oyna maydoni (eni*boyi), quantity boshqa
                area_sqm=kwargs.get('kvm', kwargs.get('area_sqm', product.kvm or product.area_sqm)),
                product_type=kwargs.get('product_type', product.product_type or 'glass'),
                note=kwargs.get('note', product.note),
            )

            product.name = payload['name']
            product.category_id = kwargs.get('category_id', product.category_id)
            product.selling_price = payload['selling_price']
            product.cost_price = payload['cost_price']
            product.quantity = payload['quantity']
            product.unit = payload['unit']
            product.eni = payload['eni']
            product.boyi = payload['boyi']
            product.kvm = payload['kvm']
            product.narx_per_kvm = payload['narx_per_kvm']
            product.width = payload['width']
            product.height = payload['height']
            product.area_sqm = payload['area_sqm']
            product.product_type = payload['product_type']
            product.note = payload['note']

            if 'barcode' in kwargs:
                product.barcode = kwargs.get('barcode')

            session.commit()

            print(f"[OK] Product updated: ID={product.id}")

            session.refresh(product)
            _ = product.category
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
        """Delete product."""
        session = Session()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                raise ValueError("Oyna topilmadi")

            if product.sale_items:
                raise ValueError("Bu mahsulot savdolarda ishlatilgan, uni o'chirib bo'lmaydi")

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
        """Update product stock. Manfiy bo'lishdan himoya."""
        session = Session()
        try:
            product = session.query(Product).options(
                joinedload(Product.category)
            ).filter_by(id=product_id).first()

            if not product:
                raise ValueError("Oyna topilmadi")

            new_qty = float(product.quantity or 0) + float(quantity_change)
            if new_qty < 0:
                raise ValueError(
                    f"Ombor manfiy bo'lib ketadi: "
                    f"mavjud={product.quantity:.4f} kvm, "
                    f"o'zgarish={quantity_change:.4f} kvm"
                )
            product.quantity = new_qty
            session.commit()

            print(f"[OK] Stock updated: ID={product_id}, Change={quantity_change}")

            session.refresh(product)
            _ = product.category
            session.expunge(product)
            return product
        except Exception as e:
            session.rollback()
            print(f"[ERROR] ProductService.update_stock: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def _validate_product_data(
        name,
        selling_price,
        cost_price,
        quantity,
        unit,
        width,
        height,
        area_sqm,
        product_type,
        note,
    ):
        """Validate and normalize product data."""
        if not name or not str(name).strip():
            raise ValueError("Oyna nomi bo'sh bo'lishi mumkin emas")

        normalized_selling_price = parse_decimal(selling_price, "Sotuv narxi")
        normalized_cost_price = parse_decimal(cost_price, "Kelgan narx", allow_zero=True)
        normalized_quantity = parse_decimal(quantity, "Ombor", allow_zero=True)

        normalized_type = (product_type or 'glass').strip().lower()
        if normalized_type not in {'glass', 'remnant'}:
            raise ValueError("Oyna turi noto'g'ri")

        normalized_unit = (unit or 'kvm').strip() or 'kvm'

        normalized_width = float(width) if width is not None else None
        normalized_height = float(height) if height is not None else None
        normalized_area = float(area_sqm) if area_sqm is not None else None
        normalized_note = str(note).strip() if note is not None and str(note).strip() else None

        if normalized_type == 'remnant' and normalized_width is not None and normalized_height is not None:
            if normalized_width <= 0:
                raise ValueError("Qoldiq oynaning eni 0 dan katta bo'lishi kerak")
            if normalized_height <= 0:
                raise ValueError("Qoldiq oynaning bo'yi 0 dan katta bo'lishi kerak")
            normalized_area = calculate_area_sqm(normalized_width, normalized_height)
            # Qoldiq oyna uchun quantity = eni*boyi (1 ta parcha)
            normalized_quantity = normalized_area

        # glass uchun quantity dialog tomonidan hisoblangan to'g'ri qiymat (eni*boyi*dona)
        # area_sqm esa bitta oynaning maydoni — quantity ni ustiga yozmaymiz
        if normalized_type == 'glass':
            # area_sqm = bitta oynaning maydoni (eni*boyi), quantity = umumiy kvm (dona*area)
            # Ikkalasini alohida saqlaymiz — quantity o'zgarmaydi
            pass

        return {
            'name': str(name).strip(),
            'selling_price': normalized_selling_price,
            'cost_price': normalized_cost_price,
            'quantity': normalized_quantity,
            'unit': normalized_unit,
            'eni': normalized_width,
            'boyi': normalized_height,
            'kvm': normalized_area,
            'narx_per_kvm': normalized_selling_price,
            'width': normalized_width,
            'height': normalized_height,
            'area_sqm': normalized_area,
            'product_type': normalized_type,
            'note': normalized_note,
        }
