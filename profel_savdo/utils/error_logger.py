# -*- coding: utf-8 -*-
"""
Error Logger Utility
Logs all exceptions to error.log file
"""
import logging
import sys
import traceback
from pathlib import Path


class ErrorLogger:
    """Error logging utility"""

    _logger = None

    @classmethod
    def get_logger(cls):
        """Get or create logger instance"""
        if cls._logger is None:
            if getattr(sys, 'frozen', False):
                app_dir = Path(sys.executable).resolve().parent
            else:
                app_dir = Path(__file__).resolve().parent.parent

            logs_dir = app_dir / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)

            # Create logger
            cls._logger = logging.getLogger("ProfelSavdo")
            cls._logger.setLevel(logging.ERROR)
            cls._logger.propagate = False

            # Create file handler
            log_file = logs_dir / "error.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.ERROR)

            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)

            existing_paths = {
                Path(handler.baseFilename).resolve()
                for handler in cls._logger.handlers
                if hasattr(handler, 'baseFilename')
            }

            if log_file.resolve() not in existing_paths:
                cls._logger.addHandler(file_handler)

        return cls._logger

    @classmethod
    def log_exception(cls, exception, context=""):
        """
        Log exception with full traceback

        Args:
            exception: Exception object
            context: Additional context string
        """
        logger = cls.get_logger()

        # Get full traceback
        tb_str = ''.join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))

        # Log with context
        if context:
            logger.error(f"[{context}] {str(exception)}\n{tb_str}")
        else:
            logger.error(f"{str(exception)}\n{tb_str}")

    @classmethod
    def log_error(cls, message, context=""):
        """
        Log error message without exception

        Args:
            message: Error message
            context: Additional context string
        """
        logger = cls.get_logger()

        if context:
            logger.error(f"[{context}] {message}")
        else:
            logger.error(message)


def log_exception(exception, context=""):
    """
    Convenience function to log exception

    Args:
        exception: Exception object
        context: Additional context string
    """
    ErrorLogger.log_exception(exception, context)


def log_error(message, context=""):
    """
    Convenience function to log error message

    Args:
        message: Error message
        context: Additional context string
    """
    ErrorLogger.log_error(message, context)


def get_user_friendly_message(exception):
    """
    Convert technical exception to user-friendly message

    Args:
        exception: Exception object

    Returns:
        User-friendly error message (str)
    """
    error_str = str(exception).lower()

    # Database errors
    if "unique constraint" in error_str or "duplicate" in error_str:
        return "Bu nom allaqachon mavjud"

    if "foreign key" in error_str:
        return "Bu yozuvni o'chirib bo'lmaydi, boshqa joyda ishlatilmoqda"

    if "not null" in error_str:
        return "Barcha majburiy maydonlarni to'ldiring"

    if "database" in error_str or "sqlite" in error_str:
        return "Ma'lumotlar bazasi xatosi"

    # Network errors
    if "connection" in error_str or "network" in error_str:
        return "Tarmoq xatosi"

    # File errors
    if "file" in error_str or "permission" in error_str:
        return "Fayl xatosi"

    # Default message
    return "Xatolik yuz berdi"
