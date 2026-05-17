# -*- coding: utf-8 -*-
"""
Main Application Entry Point
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from ui.main_window import MainWindow
from models import init_db


def main():
    try:
        # High DPI support
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setStyle('Fusion')

        # Font
        font = QFont("Segoe UI", 12)
        font.setHintingPreference(QFont.PreferFullHinting)
        app.setFont(font)

        # Initialize database
        init_db()

        # Main window
        window = MainWindow(cashier_name="Admin")
        window.showMaximized()

        sys.exit(app.exec())

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
