# -*- coding: utf-8 -*-
"""
Audit Service - Anti-Fraud Security
"""
import json
from datetime import datetime
from models.base import Session
from models.audit_log import AuditLog


class AuditService:
    """Audit logging service"""

    @staticmethod
    def log(action, user, entity_type=None, entity_id=None, details=None):
        """Log an action"""
        session = Session()
        try:
            # Convert details dict to JSON string
            details_json = json.dumps(details) if details else None

            log = AuditLog(
                action=action,
                user=user,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details_json,
                timestamp=datetime.now()
            )
            session.add(log)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Audit log error: {e}")
        finally:
            session.close()

    @staticmethod
    def get_logs(limit=100, entity_type=None, user=None):
        """Get audit logs"""
        session = Session()
        try:
            query = session.query(AuditLog).order_by(AuditLog.timestamp.desc())

            if entity_type:
                query = query.filter_by(entity_type=entity_type)
            if user:
                query = query.filter_by(user=user)

            logs = query.limit(limit).all()
            session.expunge_all()
            return logs
        finally:
            session.close()

    @staticmethod
    def log_sale_created(user, sale_id, total_amount, customer_name=None):
        """Log sale creation"""
        AuditService.log(
            action="sale_created",
            user=user,
            entity_type="sale",
            entity_id=sale_id,
            details={
                "total_amount": total_amount,
                "customer": customer_name
            }
        )

    @staticmethod
    def log_product_edited(user, product_id, product_name, changes):
        """Log product edit"""
        AuditService.log(
            action="product_edited",
            user=user,
            entity_type="product",
            entity_id=product_id,
            details={
                "product_name": product_name,
                "changes": changes
            }
        )

    @staticmethod
    def log_product_deleted(user, product_id, product_name):
        """Log product deletion"""
        AuditService.log(
            action="product_deleted",
            user=user,
            entity_type="product",
            entity_id=product_id,
            details={
                "product_name": product_name
            }
        )

    @staticmethod
    def log_debt_payment(user, customer_id, customer_name, amount):
        """Log debt payment"""
        AuditService.log(
            action="debt_paid",
            user=user,
            entity_type="debt_payment",
            entity_id=customer_id,
            details={
                "customer": customer_name,
                "amount": amount
            }
        )
