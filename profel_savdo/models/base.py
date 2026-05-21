# -*- coding: utf-8 -*-
"""
Database Base Configuration
Supports both PostgreSQL (production) and SQLite (development)
"""
from sqlalchemy import event, inspect, text
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
    run_schema_migrations()

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


def run_schema_migrations():
    """Apply lightweight schema migrations for existing databases."""
    inspector = inspect(engine)
    migrations = {
        "products": {
            "eni": "FLOAT",
            "boyi": "FLOAT",
            "kvm": "FLOAT",
            "narx_per_kvm": "FLOAT",
            "width": "FLOAT",
            "height": "FLOAT",
            "area_sqm": "FLOAT",
            "product_type": "VARCHAR(50) DEFAULT 'glass' NOT NULL",
            "note": "VARCHAR(500)",
        },
        "sale_items": {
            "eni": "FLOAT",
            "boyi": "FLOAT",
            "kvm": "FLOAT",
            "narx_per_kvm": "FLOAT",
            "width": "FLOAT",
            "height": "FLOAT",
            "area_sqm": "FLOAT",
        },
    }

    try:
        with engine.begin() as connection:
            for table_name, columns in migrations.items():
                existing_columns = {
                    column["name"] for column in inspector.get_columns(table_name)
                }
                for column_name, column_type in columns.items():
                    if column_name in existing_columns:
                        continue
                    connection.execute(
                        text(
                            f"ALTER TABLE {table_name} "
                            f"ADD COLUMN {column_name} {column_type}"
                        )
                    )

            connection.execute(
                text(
                    "UPDATE products "
                    "SET product_type = COALESCE(product_type, 'glass')"
                )
            )
            connection.execute(
                text(
                    "UPDATE products SET eni = COALESCE(eni, width)"
                )
            )
            connection.execute(
                text(
                    "UPDATE products SET boyi = COALESCE(boyi, height)"
                )
            )
            connection.execute(
                text(
                    "UPDATE products SET kvm = COALESCE(kvm, area_sqm)"
                )
            )
            connection.execute(
                text(
                    "UPDATE products SET narx_per_kvm = COALESCE(narx_per_kvm, selling_price)"
                )
            )
            connection.execute(
                text(
                    "UPDATE products SET width = COALESCE(width, eni)"
                )
            )
            connection.execute(
                text(
                    "UPDATE products SET height = COALESCE(height, boyi)"
                )
            )
            connection.execute(
                text(
                    "UPDATE products SET area_sqm = COALESCE(area_sqm, kvm)"
                )
            )
            connection.execute(
                text(
                    "UPDATE products "
                    "SET area_sqm = COALESCE(area_sqm, quantity) "
                    "WHERE product_type = 'remnant'"
                )
            )
            connection.execute(
                text(
                    "UPDATE products "
                    "SET kvm = COALESCE(kvm, area_sqm, quantity) "
                    "WHERE product_type = 'remnant'"
                )
            )
            connection.execute(
                text(
                    "UPDATE sale_items "
                    "SET area_sqm = COALESCE(area_sqm, quantity)"
                )
            )
            connection.execute(
                text(
                    "UPDATE sale_items SET eni = COALESCE(eni, width)"
                )
            )
            connection.execute(
                text(
                    "UPDATE sale_items SET boyi = COALESCE(boyi, height)"
                )
            )
            connection.execute(
                text(
                    "UPDATE sale_items SET kvm = COALESCE(kvm, area_sqm, quantity)"
                )
            )
            connection.execute(
                text(
                    "UPDATE sale_items SET narx_per_kvm = COALESCE(narx_per_kvm, price)"
                )
            )
            connection.execute(
                text(
                    "UPDATE sale_items SET width = COALESCE(width, eni)"
                )
            )
            connection.execute(
                text(
                    "UPDATE sale_items SET height = COALESCE(height, boyi)"
                )
            )
            connection.execute(
                text(
                    "UPDATE sale_items SET area_sqm = COALESCE(area_sqm, kvm, quantity)"
                )
            )
    except Exception as exc:
        print(f"Schema migration warning: {exc}")
