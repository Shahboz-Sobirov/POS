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

        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        icon_path = resolve_icon_path()
        if icon_path:
            app.setWindowIcon(QIcon(icon_path))

        font = QFont("Segoe UI", 12)
        font.setHintingPreference(QFont.PreferFullHinting)
        app.setFont(font)

        # ── 1. Ma'lumotlar bazasini BIRINCHI ishga tushirish ──────────────
        # LockPanel dan oldin init_db — DB xatosi darhol ko'rinadi
        try:
            init_db()
        except Exception as db_err:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                "Ma'lumotlar bazasi xatosi",
                f"Dastur ma'lumotlar bazasiga ulana olmadi:\n\n{db_err}\n\n"
                "Iltimos administratorga murojaat qiling."
            )
            sys.exit(1)

        # ── 2. Parol paneli ───────────────────────────────────────────────
        lock_panel = LockPanel()
        if icon_path:
            lock_panel.setWindowIcon(QIcon(icon_path))
        if lock_panel.exec() != LockPanel.Accepted:
            sys.exit(0)

        # Kassir nomini lock paneldan olish
        cashier_name = getattr(lock_panel, 'cashier_name', None) or "Admin"

        # ── 3. Asosiy oyna ────────────────────────────────────────────────
        window = MainWindow(cashier_name=cashier_name)
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
