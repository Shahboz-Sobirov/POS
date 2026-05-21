# -*- coding: utf-8 -*-
"""
Main Application Entry Point
"""
import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from ui.main_window import MainWindow
from ui.dialogs.lock_panel import LockPanel
from models import init_db


def get_app_base_dir():
    """Return the application base directory for script and frozen modes."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


def resolve_icon_path():
    """Resolve the best available icon path."""
    base_dir = get_app_base_dir()
    candidates = [
        os.path.join(base_dir, "oyna_savdo.ico"),
        os.path.join(base_dir, "icon.ico"),
        os.path.join(getattr(sys, "_MEIPASS", base_dir), "oyna_savdo.ico"),
        os.path.join(getattr(sys, "_MEIPASS", base_dir), "icon.ico"),
        os.path.join(os.path.dirname(base_dir), "oyna_savdo.ico"),
        os.path.join(os.path.dirname(base_dir), "29.ico"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


def set_windows_app_id():
    """Set Windows AppUserModelID so taskbar uses the correct icon."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "oyna.savdo.pos.app"
        )
    except Exception:
        pass


def main():
    try:
        set_windows_app_id()

        # High DPI support
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        icon_path = resolve_icon_path()
        if icon_path:
            app.setWindowIcon(QIcon(icon_path))

        # Font
        font = QFont("Segoe UI", 12)
        font.setHintingPreference(QFont.PreferFullHinting)
        app.setFont(font)

        lock_panel = LockPanel()
        if icon_path:
            lock_panel.setWindowIcon(QIcon(icon_path))
        if lock_panel.exec() != LockPanel.Accepted:
            sys.exit(0)

        # Initialize database
        init_db()

        # Main window
        window = MainWindow(cashier_name="Admin")
        if icon_path:
            window.setWindowIcon(QIcon(icon_path))
        window.showMaximized()

        sys.exit(app.exec())

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
