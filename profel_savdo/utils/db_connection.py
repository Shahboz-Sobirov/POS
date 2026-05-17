# -*- coding: utf-8 -*-
"""
Database Connection Manager
Handles PostgreSQL and SQLite connections with fallback support
"""
import json
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, DatabaseError
from sqlalchemy.pool import NullPool


class DatabaseConfig:
    """Database configuration manager"""

    def __init__(self, config_path=None):
        if config_path is None:
            # For PyInstaller compatibility
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                app_dir = os.path.dirname(sys.executable)
            else:
                # Running as script
                app_dir = os.path.dirname(os.path.dirname(__file__))

            config_path = os.path.join(app_dir, 'config', 'database.json')
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        """Load database configuration from JSON file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Default configuration
                return {
                    "database_type": "sqlite",
                    "host": "localhost",
                    "port": 5432,
                    "database": "profel_savdo",
                    "username": "postgres",
                    "password": "",
                    "fallback_to_sqlite": True,
                    "sqlite_file": "profel_savdo.db"
                }
        except Exception as e:
            print(f"Error loading database config: {e}")
            return self.get_default_config()

    def save_config(self, config):
        """Save database configuration to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.config = config
            return True
        except Exception as e:
            print(f"Error saving database config: {e}")
            return False

    def get_default_config(self):
        """Get default SQLite configuration"""
        return {
            "database_type": "sqlite",
            "fallback_to_sqlite": True,
            "sqlite_file": "profel_savdo.db"
        }

    def get_postgresql_url(self):
        """Build PostgreSQL connection URL"""
        username = self.config.get('username', 'postgres')
        password = self.config.get('password', '')
        host = self.config.get('host', 'localhost')
        port = self.config.get('port', 5432)
        database = self.config.get('database', 'profel_savdo')

        if password:
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        else:
            return f"postgresql://{username}@{host}:{port}/{database}"

    def get_sqlite_url(self):
        """Build SQLite connection URL"""
        sqlite_file = self.config.get('sqlite_file', 'profel_savdo.db')

        # For PyInstaller compatibility - use executable directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.dirname(__file__))

        db_path = os.path.join(app_dir, sqlite_file)
        return f"sqlite:///{db_path}"


class DatabaseConnection:
    """Database connection manager with fallback support"""

    def __init__(self):
        self.config_manager = DatabaseConfig()
        self.engine = None
        self.connection_type = None
        self.last_error = None

    def test_connection(self, connection_url, timeout=5):
        """Test database connection"""
        try:
            # Create test engine with short timeout
            test_engine = create_engine(
                connection_url,
                poolclass=NullPool,
                connect_args={'connect_timeout': timeout} if 'postgresql' in connection_url else {}
            )

            # Try to connect
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            test_engine.dispose()
            return True, None
        except OperationalError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            return False, error_msg
        except DatabaseError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            return False, error_msg
        except Exception as e:
            return False, str(e)

    def connect(self):
        """Connect to database with fallback support"""
        config = self.config_manager.config
        db_type = config.get('database_type', 'sqlite')

        # Try PostgreSQL first if configured
        if db_type == 'postgresql':
            postgresql_url = self.config_manager.get_postgresql_url()
            success, error = self.test_connection(postgresql_url)

            if success:
                self.engine = create_engine(
                    postgresql_url,
                    pool_pre_ping=True,
                    pool_size=10,
                    max_overflow=20,
                    echo=False
                )
                self.connection_type = 'postgresql'
                self.last_error = None
                print(f"[OK] Connected to PostgreSQL: {config.get('host')}:{config.get('port')}/{config.get('database')}")
                return True, 'postgresql'
            else:
                self.last_error = error
                print(f"[ERROR] PostgreSQL connection failed: {error}")

                # Fallback to SQLite if enabled
                if config.get('fallback_to_sqlite', True):
                    print("[WARNING] Falling back to SQLite...")
                    return self._connect_sqlite()
                else:
                    return False, error

        # Use SQLite directly
        else:
            return self._connect_sqlite()

    def reconnect(self, config=None):
        """Reconnect using the current or provided configuration."""
        old_engine = self.engine
        old_connection_type = self.connection_type
        old_last_error = self.last_error
        old_config = dict(self.config_manager.config)

        if config is not None:
            self.config_manager.config = dict(config)

        self.engine = None
        self.connection_type = None
        self.last_error = None

        success, conn_type = self.connect()
        if success:
            if old_engine is not None and old_engine is not self.engine:
                try:
                    old_engine.dispose()
                except Exception:
                    pass
            return True, conn_type

        self.config_manager.config = old_config
        self.engine = old_engine
        self.connection_type = old_connection_type
        self.last_error = old_last_error
        return False, self.last_error

    def _connect_sqlite(self):
        """Connect to SQLite database"""
        try:
            sqlite_url = self.config_manager.get_sqlite_url()
            self.engine = create_engine(sqlite_url, echo=False)
            self.connection_type = 'sqlite'
            self.last_error = None
            print(f"[OK] Connected to SQLite: {self.config_manager.config.get('sqlite_file')}")
            return True, 'sqlite'
        except Exception as e:
            self.last_error = str(e)
            print(f"[ERROR] SQLite connection failed: {e}")
            return False, str(e)

    def get_engine(self):
        """Get database engine"""
        if self.engine is None:
            self.connect()
        return self.engine

    def get_connection_info(self):
        """Get current connection information"""
        return {
            'type': self.connection_type,
            'config': self.config_manager.config,
            'last_error': self.last_error
        }

    def is_postgresql(self):
        """Check if using PostgreSQL"""
        return self.connection_type == 'postgresql'

    def is_sqlite(self):
        """Check if using SQLite"""
        return self.connection_type == 'sqlite'


# Global connection instance
_db_connection = None


def get_db_connection():
    """Get global database connection instance"""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


def test_postgresql_connection(host, port, database, username, password):
    """Test PostgreSQL connection with given parameters"""
    try:
        if password:
            url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        else:
            url = f"postgresql://{username}@{host}:{port}/{database}"

        test_engine = create_engine(
            url,
            poolclass=NullPool,
            connect_args={'connect_timeout': 5}
        )

        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        test_engine.dispose()
        return True, "Muvaffaqiyatli ulanildi!"
    except OperationalError as e:
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        if 'password authentication failed' in error_msg.lower():
            return False, "Parol noto'g'ri"
        elif 'could not connect' in error_msg.lower() or 'connection refused' in error_msg.lower():
            return False, "Server bilan aloqa yo'q. IP manzil va portni tekshiring."
        elif 'database' in error_msg.lower() and 'does not exist' in error_msg.lower():
            return False, "Database topilmadi. Avval database yarating."
        else:
            return False, f"Ulanish xatosi: {error_msg}"
    except Exception as e:
        return False, f"Xatolik: {str(e)}"
