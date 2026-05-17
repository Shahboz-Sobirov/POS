# -*- coding: utf-8 -*-
"""
Database Base Configuration
Supports both PostgreSQL (production) and SQLite (development)
"""
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from utils.db_connection import get_db_connection

# Get database connection
db_conn = get_db_connection()
success, conn_type = db_conn.connect()

if not success:
    print(f"[WARNING] Database connection failed: {db_conn.last_error}")
    print("[WARNING] Application may not work correctly")

# Get engine from connection manager
engine = db_conn.get_engine()

def _attach_sqlite_pragma(target_engine):
    """Enable foreign keys whenever SQLite is active."""
    if target_engine is None or target_engine.dialect.name != "sqlite":
        return
    if getattr(target_engine, "_sqlite_pragma_attached", False):
        return

    @event.listens_for(target_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    target_engine._sqlite_pragma_attached = True


_attach_sqlite_pragma(engine)

# Create scoped session factory - thread-safe
session_factory = sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=False)
Session = scoped_session(session_factory)

# Create base class
Base = declarative_base()


def get_session():
    """Get a new database session"""
    return Session()


def close_session():
    """Close current session"""
    Session.remove()


def reconnect_database():
    """Reconnect the active SQLAlchemy engine/session without restarting the app."""
    global engine

    Session.remove()
    success, conn_type = db_conn.reconnect()
    if not success:
        return False, db_conn.last_error

    engine = db_conn.get_engine()
    Session.configure(bind=engine)
    _attach_sqlite_pragma(engine)
    init_db()
    return True, conn_type


def init_db():
    """Initialize database tables"""
    from models.category import Category
    from models.product import Product
    from models.customer import Customer
    from models.sale import Sale, SaleItem
    from models.debt_payment import DebtPayment
    from models.audit_log import AuditLog

    Base.metadata.create_all(engine)

    # Create default categories if not exist
    from config.constants import DEFAULT_CATEGORIES
    session = Session()
    try:
        existing_categories = session.query(Category).count()
        if existing_categories == 0:
            for cat_data in DEFAULT_CATEGORIES:
                category = Category(
                    name=cat_data['name'],
                    color=cat_data['color'],
                    icon=cat_data.get('icon', '📦')
                )
                session.add(category)
            session.commit()
            print(f"[OK] Created {len(DEFAULT_CATEGORIES)} default categories")
    except Exception as e:
        session.rollback()
        print(f"Error creating default categories: {e}")
    finally:
        Session.remove()
