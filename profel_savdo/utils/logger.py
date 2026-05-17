# -*- coding: utf-8 -*-
"""
Application Logger
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


class AppLogger:
    """Application logging system"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        """Setup logging configuration"""
        if getattr(sys, 'frozen', False):
            app_dir = Path(sys.executable).resolve().parent
        else:
            app_dir = Path(__file__).resolve().parent.parent

        logs_dir = app_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self._logger = logging.getLogger("ProfelSavdo")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        # File handler for errors
        error_log_path = logs_dir / "error.log"
        error_handler = logging.FileHandler(error_log_path, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)

        # File handler for all logs
        app_log_path = logs_dir / "app.log"
        app_handler = logging.FileHandler(app_log_path, encoding='utf-8')
        app_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(formatter)
        app_handler.setFormatter(formatter)

        existing_paths = {
            Path(handler.baseFilename).resolve()
            for handler in self._logger.handlers
            if hasattr(handler, 'baseFilename')
        }

        if error_log_path.resolve() not in existing_paths:
            self._logger.addHandler(error_handler)
        if app_log_path.resolve() not in existing_paths:
            self._logger.addHandler(app_handler)

    def log_error(self, page, action, exception):
        """
        Log error with context

        Args:
            page: Page name where error occurred
            action: User action that caused error
            exception: Exception object
        """
        import traceback

        error_msg = f"""
{'='*60}
PAGE: {page}
ACTION: {action}
TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
ERROR: {type(exception).__name__}: {str(exception)}
{'='*60}
TRACEBACK:
{''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))}
{'='*60}
"""
        self._logger.error(error_msg)

    def log_info(self, message):
        """Log info message"""
        self._logger.info(message)

    def log_warning(self, message):
        """Log warning message"""
        self._logger.warning(message)


# Singleton instance
logger = AppLogger()
