# -*- coding: utf-8 -*-
"""
Customer Service
"""
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from models.base import Session
from models.customer import Customer
from models.sale import Sale, SaleItem
from models.debt_payment import DebtPayment


class CustomerService:
    """Customer business logic"""

    @staticmethod
    def get_all():
        """Get all customers"""
        session = Session()
        try:
            customers = session.query(Customer).order_by(Customer.full_name).all()
            session.expunge_all()
            return customers
        except Exception as e:
            print(f"[ERROR] CustomerService.get_all: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_by_id(customer_id):
        """Get customer by ID"""
        session = Session()
        try:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if customer:
                session.expunge(customer)
            return customer
        except Exception as e:
            print(f"[ERROR] CustomerService.get_by_id: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def search(query):
        """Search customers by name or phone"""
        session = Session()
        try:
            customers = session.query(Customer).filter(
                (Customer.full_name.ilike(f'%{query}%')) |
                (Customer.phone.ilike(f'%{query}%'))
            ).order_by(Customer.full_name).all()
            session.expunge_all()
            return customers
        except Exception as e:
            print(f"[ERROR] CustomerService.search: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def create(full_name, phone=None):
        """Create new customer"""
        session = Session()
        try:
            customer = Customer(full_name=full_name, phone=phone)
            session.add(customer)
            session.commit()

            print(f"[OK] Customer created: ID={customer.id}, Name={customer.full_name}")

            session.refresh(customer)
            session.expunge(customer)
            return customer
        except Exception as e:
            session.rollback()
            print(f"[ERROR] CustomerService.create: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def update(customer_id, full_name=None, phone=None):
        """Update customer"""
        session = Session()
        try:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                raise ValueError("Customer not found")

            if full_name is not None:
                customer.full_name = full_name
            if phone is not None:
                customer.phone = phone

            session.commit()

            print(f"[OK] Customer updated: ID={customer.id}")

            session.refresh(customer)
            session.expunge(customer)
            return customer
        except Exception as e:
            session.rollback()
            print(f"[ERROR] CustomerService.update: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def delete(customer_id):
        """Delete customer"""
        session = Session()
        try:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                raise ValueError("Customer not found")

            session.delete(customer)
            session.commit()

            print(f"[OK] Customer deleted: ID={customer_id}")
        except Exception as e:
            session.rollback()
            print(f"[ERROR] CustomerService.delete: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def update_debt(customer_id, debt_change):
        """Update customer debt"""
        session = Session()
        try:
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                raise ValueError("Customer not found")

            customer.total_debt += debt_change
            session.commit()

            print(f"[OK] Customer debt updated: ID={customer_id}, Change={debt_change}")

            session.refresh(customer)
            session.expunge(customer)
            return customer
        except Exception as e:
            session.rollback()
            print(f"[ERROR] CustomerService.update_debt: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_customer_sales(customer_id):
        """Get all sales for a customer with related items preloaded"""
        session = Session()
        try:
            sales = session.query(Sale).options(
                joinedload(Sale.items).joinedload(SaleItem.product),
                joinedload(Sale.customer)
            ).filter_by(
                customer_id=customer_id
            ).order_by(Sale.sale_date.desc()).all()
            session.expunge_all()
            return sales
        except Exception as e:
            print(f"[ERROR] CustomerService.get_customer_sales: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_customer_debt_payments(customer_id):
        """Get all debt payments for a customer"""
        session = Session()
        try:
            payments = session.query(DebtPayment).filter_by(customer_id=customer_id).order_by(DebtPayment.payment_date.desc()).all()
            session.expunge_all()
            return payments
        except Exception as e:
            print(f"[ERROR] CustomerService.get_customer_debt_payments: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_customers_with_debt():
        """Get customers with debt, sorted by oldest debt first"""
        debt_overview = CustomerService.get_customers_with_debt_overview()
        return [row['customer'] for row in debt_overview]

    @staticmethod
    def get_customer_overview(query=None):
        """Get customers with last sale date and total sales count"""
        session = Session()
        try:
            customer_query = session.query(
                Customer,
                func.max(Sale.sale_date).label('last_sale_date'),
                func.count(Sale.id).label('total_sales')
            ).outerjoin(
                Sale, Sale.customer_id == Customer.id
            )

            if query:
                search = f'%{query}%'
                customer_query = customer_query.filter(
                    (Customer.full_name.ilike(search)) |
                    (Customer.phone.ilike(search))
                )

            rows = customer_query.group_by(Customer.id).order_by(Customer.full_name).all()
            overview = [
                {
                    'customer': customer,
                    'last_sale_date': last_sale_date,
                    'total_sales': int(total_sales or 0),
                }
                for customer, last_sale_date, total_sales in rows
            ]
            session.expunge_all()
            return overview
        except Exception as e:
            print(f"[ERROR] CustomerService.get_customer_overview: {e}")
            raise e
        finally:
            Session.remove()

    @staticmethod
    def get_customers_with_debt_overview():
        """Get indebted customers with oldest sale date in one query"""
        session = Session()
        try:
            rows = session.query(
                Customer,
                func.min(Sale.sale_date).label('oldest_sale_date')
            ).outerjoin(
                Sale, Sale.customer_id == Customer.id
            ).filter(
                Customer.total_debt > 0
            ).group_by(
                Customer.id
            ).order_by(
                func.min(Sale.sale_date).asc().nullslast(),
                Customer.full_name.asc()
            ).all()

            overview = [
                {
                    'customer': customer,
                    'oldest_sale_date': oldest_sale_date,
                }
                for customer, oldest_sale_date in rows
            ]
            session.expunge_all()
            return overview
        except Exception as e:
            print(f"[ERROR] CustomerService.get_customers_with_debt_overview: {e}")
            raise e
        finally:
            Session.remove()
