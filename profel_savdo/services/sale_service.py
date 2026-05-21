# -*- coding: utf-8 -*-
"""
Sale Service
"""
from datetime import datetime
from models.base import Session
from models.sale import Sale, SaleItem
from models.product import Product
from models.customer import Customer
from services.audit_service import AuditService
from utils.formatter import parse_decimal


class SaleService:
    """Sale business logic"""

    @staticmethod
    def create_sale(customer_id, payment_type, items, payment_breakdown=None, cashier="Admin"):
        """
        Create new sale with automatic profit calculation.
        Barcha tekshiruv va yozuv BIR session ichida amalga oshiriladi.
        """
        session = Session()
        try:
            total_amount = 0.0
            total_profit = 0.0

            # ── 1-qadam: mahsulotlarni yuklash, tekshirish ──────────────
            prepared = []  # (product_obj, eni, boyi, kvm, price, cost_price)

            for item_data in items:
                product = session.query(Product).filter_by(
                    id=item_data['product_id']
                ).with_for_update().first()   # lock — parallel savdolardan himoya

                if not product:
                    raise ValueError(f"Oyna topilmadi: ID={item_data['product_id']}")

                eni, boyi, kvm = SaleService._extract_dimensions(item_data)

                if kvm <= 0:
                    raise ValueError(f"'{product.name}' uchun KVM 0 dan katta bo'lishi kerak")

                price = parse_decimal(
                    item_data.get('narx_per_kvm', item_data.get('price', 0)),
                    "Narx/KVM"
                )
                if price <= 0:
                    raise ValueError(f"'{product.name}' uchun narx 0 dan katta bo'lishi kerak")

                if kvm > product.quantity:
                    raise ValueError(
                        f"'{product.name}': omborda {product.quantity:.4f} kvm bor, "
                        f"lekin {kvm:.4f} kvm so'raldi"
                    )

                cost = float(product.cost_price or 0)
                total_amount += price * kvm
                total_profit += (price - cost) * kvm

                prepared.append((product, eni, boyi, kvm, price, cost))

            # ── 2-qadam: savdo yaratish ──────────────────────────────────
            sale = Sale(
                customer_id=customer_id,
                total_amount=total_amount,
                payment_type=payment_type,
                payment_breakdown=payment_breakdown,
                profit=total_profit,
                cashier=cashier,
                sale_date=datetime.now()
            )
            session.add(sale)
            session.flush()  # sale.id olish uchun

            # ── 3-qadam: qatorlar yozish + ombor kamaytirish ─────────────
            for product, eni, boyi, kvm, price, cost in prepared:
                item_profit = (price - cost) * kvm

                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=kvm,
                    eni=eni,
                    boyi=boyi,
                    kvm=kvm,
                    narx_per_kvm=price,
                    width=eni,
                    height=boyi,
                    area_sqm=kvm,
                    price=price,
                    cost_price=cost,
                    profit=item_profit
                )
                session.add(sale_item)

                # Ombor kamaytirish — manfiy bo'lishdan himoya
                product.quantity = max(product.quantity - kvm, 0)

            # ── 4-qadam: qarz yangilash ──────────────────────────────────
            if customer_id and payment_breakdown:
                qarz = float(payment_breakdown.get('qarz', 0) or 0)
                if qarz > 0:
                    customer = session.query(Customer).filter_by(id=customer_id).first()
                    if customer:
                        customer.total_debt = (customer.total_debt or 0) + qarz

            session.commit()
            session.refresh(sale)

            # ── 5-qadam: audit log (session commit dan KEYIN) ─────────────
            # expunge DAN OLDIN customer query qilamiz — session hali ochiq
            customer_name = None
            if customer_id:
                cust = session.query(Customer).filter_by(id=customer_id).first()
                if cust:
                    customer_name = cust.full_name

            session.expunge(sale)

            try:
                AuditService.log_sale_created(cashier, sale.id, total_amount, customer_name)
            except Exception:
                pass  # Audit log xatosi savdoni bloklamamasligi kerak

            return sale

        except Exception as e:
            session.rollback()
            raise e
        finally:
            Session.remove()  # scoped session uchun to'g'ri yopish usuli

    # ── Dimension extractor ───────────────────────────────────────────────

    @staticmethod
    def _extract_dimensions(item_data):
        """
        cart_item dict dan eni, boyi, kvm oladi.
        Agar eni va boyi berilgan bo'lsa — kvm = eni*boyi (1 ta oyna).
        Savat allaqachon to'g'ri kvm ni yuboradi, shuning uchun
        eni*boyi qayta hisoblanmaydi — cart kvm qiymati ishlatiladi.
        """
        eni = item_data.get('eni') or item_data.get('width')
        boyi = item_data.get('boyi') or item_data.get('height')

        # Savatdagi kvm allaqachon to'g'ri (GlassOrderDialog tomonidan hisoblangan)
        kvm_raw = item_data.get('kvm') or item_data.get('area_sqm') or item_data.get('quantity')
        kvm = parse_decimal(kvm_raw, "KVM")

        if eni is not None:
            eni = float(eni)
        if boyi is not None:
            boyi = float(boyi)

        return eni, boyi, kvm

    # ── To'liq o'qish metodlari ───────────────────────────────────────────

    @staticmethod
    def get_all(limit=100):
        session = Session()
        try:
            sales = session.query(Sale).order_by(
                Sale.sale_date.desc()
            ).limit(limit).all()
            session.expunge_all()
            return sales
        finally:
            Session.remove()

    @staticmethod
    def get_by_id(sale_id):
        session = Session()
        try:
            sale = session.query(Sale).filter_by(id=sale_id).first()
            if sale:
                session.expunge(sale)
            return sale
        finally:
            Session.remove()

    @staticmethod
    def get_by_date_range(start_date, end_date):
        from sqlalchemy.orm import joinedload
        session = Session()
        try:
            sales = session.query(Sale).options(
                joinedload(Sale.customer),
                joinedload(Sale.items).joinedload(SaleItem.product)
            ).filter(
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date
            ).order_by(Sale.sale_date.desc()).all()
            session.expunge_all()
            return sales
        finally:
            Session.remove()

    @staticmethod
    def get_daily_report(date):
        session = Session()
        try:
            start = datetime.combine(date, datetime.min.time())
            end   = datetime.combine(date, datetime.max.time())

            sales = session.query(Sale).filter(
                Sale.sale_date >= start,
                Sale.sale_date <= end
            ).order_by(Sale.sale_date.desc()).all()

            total_revenue = sum(s.total_amount for s in sales)
            total_profit  = sum(s.profit for s in sales)

            payment_totals = {'naqd': 0, 'karta': 0, 'click': 0, 'qarz': 0}
            for sale in sales:
                if sale.payment_breakdown:
                    for key, value in sale.payment_breakdown.items():
                        if key in payment_totals:
                            payment_totals[key] += float(value or 0)

            session.expunge_all()
            return {
                'sales': sales,
                'total_sales': len(sales),
                'total_revenue': total_revenue,
                'total_profit': total_profit,
                'payment_totals': payment_totals,
            }
        finally:
            Session.remove()

    @staticmethod
    def update_stock(product_id, quantity_change):
        """
        Ombor miqdorini o'zgartirish.
        Manfiy o'zgarishda ham 0 dan pastga tushmaydi.
        """
        session = Session()
        try:
            from sqlalchemy.orm import joinedload
            product = session.query(Product).options(
                joinedload(Product.category)
            ).filter_by(id=product_id).first()

            if not product:
                raise ValueError("Oyna topilmadi")

            new_qty = float(product.quantity or 0) + float(quantity_change)
            if new_qty < 0:
                raise ValueError(
                    f"Ombor manfiy bo'lib ketadi: "
                    f"mavjud={product.quantity:.4f}, o'zgarish={quantity_change:.4f}"
                )
            product.quantity = new_qty
            session.commit()

            session.refresh(product)
            _ = product.category
            session.expunge(product)
            return product
        except Exception as e:
            session.rollback()
            raise e
        finally:
            Session.remove()  # update_stock uchun ham Session.remove()
