# -*- coding: utf-8 -*-
"""
Sale Service
"""
import json
from datetime import datetime
from models.base import Session
from models.sale import Sale, SaleItem
from models.product import Product
from models.customer import Customer
from services.audit_service import AuditService
from utils.formatter import calculate_window_metrics, parse_decimal


class SaleService:
    """Sale business logic"""

    @staticmethod
    def create_sale(customer_id, payment_type, items, payment_breakdown=None, cashier="Admin"):
        """
        Create new sale with automatic profit calculation

        Args:
            customer_id: Customer ID (can be None)
            payment_type: Payment type string
            items: List of dicts with product_id, quantity, price
            payment_breakdown: Dict with payment breakdown (naqd, karta, click, qarz)
            cashier: Cashier name
        """
        session = Session()
        try:
            # Calculate totals FIRST before creating sale
            total_amount = 0
            total_profit = 0

            # Pre-calculate totals from items
            for item_data in items:
                product = session.query(Product).filter_by(id=item_data['product_id']).first()
                if not product:
                    raise ValueError(f"Oyna topilmadi: {item_data['product_id']}")

                item = SaleService._normalize_glass_item(item_data)
                eni = item['eni']
                boyi = item['boyi']
                kvm = item['kvm']
                quantity = item['quantity']
                price = item['narx_per_kvm']
                cost_price = product.cost_price

                if kvm <= 0:
                    raise ValueError("Oyna kvm 0 dan katta bo'lishi kerak")

                if quantity > product.quantity:
                    raise ValueError(f"{product.name} uchun omborda yetarli kvm yo'q")

                # Calculate totals
                total_amount += price * kvm
                total_profit += (price - cost_price) * kvm

            # Create sale with calculated totals
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
            session.flush()  # Get sale ID

            # Add items and update stock
            for item_data in items:
                product = session.query(Product).filter_by(id=item_data['product_id']).first()

                item = SaleService._normalize_glass_item(item_data)
                eni = item['eni']
                boyi = item['boyi']
                kvm = item['kvm']
                quantity = item['quantity']
                price = item['narx_per_kvm']
                cost_price = product.cost_price
                item_profit = (price - cost_price) * kvm

                # Create sale item
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=quantity,
                    eni=eni,
                    boyi=boyi,
                    kvm=kvm,
                    narx_per_kvm=price,
                    width=eni,
                    height=boyi,
                    area_sqm=kvm,
                    price=price,
                    cost_price=cost_price,
                    profit=item_profit
                )
                session.add(sale_item)

                # Update stock
                product.quantity -= kvm

            # Update customer debt if needed
            if customer_id and payment_breakdown and payment_breakdown.get('qarz', 0) > 0:
                customer = session.query(Customer).filter_by(id=customer_id).first()
                if customer:
                    customer.total_debt += payment_breakdown['qarz']

            session.commit()
            session.refresh(sale)
            session.expunge(sale)

            # Audit log
            customer_name = None
            if customer_id:
                customer = session.query(Customer).filter_by(id=customer_id).first()
                if customer:
                    customer_name = customer.full_name

            AuditService.log_sale_created(cashier, sale.id, total_amount, customer_name)

            return sale

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def get_all(limit=100):
        """Get all sales"""
        session = Session()
        try:
            sales = session.query(Sale).order_by(Sale.sale_date.desc()).limit(limit).all()
            session.expunge_all()
            return sales
        finally:
            session.close()

    @staticmethod
    def _normalize_glass_item(item_data):
        """Normalize new Uzbek glass fields while keeping legacy callers working."""
        eni_raw = item_data.get('eni', item_data.get('width'))
        boyi_raw = item_data.get('boyi', item_data.get('height'))

        explicit_kvm = item_data.get('kvm', item_data.get('area_sqm', item_data.get('quantity')))
        eni = None
        boyi = None

        if eni_raw is not None and boyi_raw is not None:
            metrics = calculate_window_metrics(eni_raw, boyi_raw)
            eni = metrics['eni']
            boyi = metrics['boyi']
            kvm = metrics['kvm']
        else:
            kvm = parse_decimal(explicit_kvm, "KVM")

        if kvm <= 0:
            raise ValueError("Oyna kvm 0 dan katta bo'lishi kerak")

        price = parse_decimal(
            item_data.get('narx_per_kvm', item_data.get('price', 0)),
            "Narx/KVM"
        )
        if price <= 0:
            raise ValueError("Narx/kvm 0 dan katta bo'lishi kerak")

        return {
            'eni': eni,
            'boyi': boyi,
            'kvm': kvm,
            'quantity': kvm,
            'narx_per_kvm': price,
        }

    @staticmethod
    def get_by_id(sale_id):
        """Get sale by ID"""
        session = Session()
        try:
            sale = session.query(Sale).filter_by(id=sale_id).first()
            if sale:
                session.expunge(sale)
            return sale
        finally:
            session.close()

    @staticmethod
    def get_by_date_range(start_date, end_date):
        """Get sales by date range with eager loading"""
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

            # Detach from session to avoid lazy loading issues
            session.expunge_all()
            return sales
        finally:
            session.close()

    @staticmethod
    def get_daily_report(date):
        """Get daily sales report"""
        session = Session()
        try:
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())

            sales = session.query(Sale).filter(
                Sale.sale_date >= start,
                Sale.sale_date <= end
            ).order_by(Sale.sale_date.desc()).all()

            # Calculate totals
            total_sales = len(sales)
            total_revenue = sum(s.total_amount for s in sales)
            total_profit = sum(s.profit for s in sales)

            # Payment breakdown
            payment_totals = {
                'naqd': 0,
                'karta': 0,
                'click': 0,
                'qarz': 0
            }

            for sale in sales:
                if sale.payment_breakdown:
                    for key, value in sale.payment_breakdown.items():
                        if key in payment_totals:
                            payment_totals[key] += value

            session.expunge_all()

            return {
                'sales': sales,
                'total_sales': total_sales,
                'total_revenue': total_revenue,
                'total_profit': total_profit,
                'payment_totals': payment_totals
            }
        finally:
            session.close()
