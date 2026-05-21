# -*- coding: utf-8 -*-
"""
Debt Payment Service
"""
import json
from datetime import datetime
from sqlalchemy.orm import joinedload
from models.base import Session
from models.debt_payment import DebtPayment
from models.customer import Customer
from services.audit_service import AuditService


class DebtPaymentService:
    """Debt payment business logic"""

    @staticmethod
    def normalize_payment_breakdown(payment_breakdown):
        """Return payment breakdown as a clean dictionary."""
        if not payment_breakdown:
            return {}

        if isinstance(payment_breakdown, dict):
            return payment_breakdown

        if isinstance(payment_breakdown, str):
            try:
                parsed = json.loads(payment_breakdown)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}

        return {}

    @staticmethod
    def create_payment(customer_id, amount, payment_type, payment_breakdown=None, note=None, cashier="Admin"):
        """
        Create debt payment

        Args:
            customer_id: Customer ID
            amount: Payment amount
            payment_type: Payment type (Naqd, Karta, Click, Mixed)
            payment_breakdown: Dict with payment breakdown
            note: Optional note
            cashier: Cashier name
        """
        session = Session()
        try:
            # Get customer
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                raise ValueError("Customer not found")

            normalized_breakdown = DebtPaymentService.normalize_payment_breakdown(payment_breakdown)

            # Create payment
            payment = DebtPayment(
                customer_id=customer_id,
                amount=amount,
                payment_type=payment_type,
                payment_breakdown=json.dumps(normalized_breakdown) if normalized_breakdown else None,
                note=note,
                payment_date=datetime.now()
            )
            session.add(payment)

            # Update customer debt
            customer.total_debt -= amount
            if customer.total_debt < 0:
                customer.total_debt = 0

            session.commit()
            session.refresh(payment)
            payment.payment_breakdown = normalized_breakdown
            session.expunge(payment)

            # Audit log
            AuditService.log_debt_payment(cashier, customer_id, customer.full_name, amount)

            return payment

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def get_all(limit=100):
        """Get all debt payments"""
        session = Session()
        try:
            payments = session.query(DebtPayment).options(
                joinedload(DebtPayment.customer)
            ).order_by(DebtPayment.payment_date.desc()).limit(limit).all()
            for payment in payments:
                payment.payment_breakdown = DebtPaymentService.normalize_payment_breakdown(
                    payment.payment_breakdown
                )
            session.expunge_all()
            return payments
        finally:
            session.close()

    @staticmethod
    def get_by_customer(customer_id):
        """Get debt payments by customer"""
        session = Session()
        try:
            payments = session.query(DebtPayment).options(
                joinedload(DebtPayment.customer)
            ).filter_by(customer_id=customer_id).order_by(DebtPayment.payment_date.desc()).all()
            for payment in payments:
                payment.payment_breakdown = DebtPaymentService.normalize_payment_breakdown(
                    payment.payment_breakdown
                )
            session.expunge_all()
            return payments
        finally:
            session.close()

    @staticmethod
    def get_by_date_range(start_date, end_date):
        """Get debt payments by date range"""
        session = Session()
        try:
            payments = session.query(DebtPayment).options(
                joinedload(DebtPayment.customer)
            ).filter(
                DebtPayment.payment_date >= start_date,
                DebtPayment.payment_date <= end_date
            ).order_by(DebtPayment.payment_date.desc()).all()
            for payment in payments:
                payment.payment_breakdown = DebtPaymentService.normalize_payment_breakdown(
                    payment.payment_breakdown
                )
            session.expunge_all()
            return payments
        finally:
            session.close()
