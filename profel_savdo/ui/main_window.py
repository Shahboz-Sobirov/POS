# -*- coding: utf-8 -*-
"""
Main Window - Profel Savdo
"""
import sys
from datetime import datetime
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QStackedWidget, QLabel, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from config.constants import APP_NAME, WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from ui.shortcuts import ShortcutManager
from ui.theme import get_stylesheet
from ui.pages.sales_page import SalesPage
from ui.pages.products_page import ProductsPage
from ui.pages.customers_page import CustomersPage
from ui.pages.reports_page import ReportsPage
from ui.pages.debt_payment_page import DebtPaymentPage
from ui.pages.categories_page import CategoriesPage
from ui.pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self, cashier_name="Admin"):
        super().__init__()
        self.cashier_name = cashier_name
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Apply theme
        self.setStyleSheet(get_stylesheet())

        self.setup_ui()
        self.setup_shortcuts()
        self.setup_clock()

        # Default page: SOTUV (not dashboard)
        self.switch_page(0)

    def setup_ui(self):
        """Setup UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Top bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Content layout (sidebar + pages)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = self.create_sidebar()
        content_layout.addWidget(sidebar)

        # Content area
        self.content_stack = QStackedWidget()

        # Pages
        self.sales_page = SalesPage(self.cashier_name)
        self.products_page = ProductsPage()
        self.customers_page = CustomersPage()
        self.reports_page = ReportsPage()
        self.debt_payment_page = DebtPaymentPage(self.cashier_name)
        self.categories_page = CategoriesPage()
        self.settings_page = SettingsPage()

        self.content_stack.addWidget(self.sales_page)  # 0 - F1
        self.content_stack.addWidget(self.products_page)  # 1 - F2
        self.content_stack.addWidget(self.customers_page)  # 2 - F3
        self.content_stack.addWidget(self.reports_page)  # 3 - F4
        self.content_stack.addWidget(self.debt_payment_page)  # 4 - F5
        self.content_stack.addWidget(self.categories_page)  # 5 - F6
        self.content_stack.addWidget(self.settings_page)  # 6 - F7

        content_layout.addWidget(self.content_stack)

        main_layout.addLayout(content_layout)

        central_widget.setLayout(main_layout)

    def create_top_bar(self):
        """Create top bar"""
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(60)

        layout = QHBoxLayout()
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        # App title
        title_label = QLabel(f"🏢 {APP_NAME}")
        title_label.setObjectName("appTitle")
        layout.addWidget(title_label)

        layout.addStretch()

        # Clock
        self.clock_label = QLabel()
        self.clock_label.setObjectName("clockLabel")
        layout.addWidget(self.clock_label)

        # User
        user_label = QLabel(f"👤 {self.cashier_name}")
        user_label.setObjectName("userLabel")
        layout.addWidget(user_label)

        # Shortcut helper
        shortcut_label = QLabel("F1-F7: Sahifalar | F8: Chek | F12: Savdo")
        shortcut_label.setObjectName("userLabel")
        layout.addWidget(shortcut_label)

        top_bar.setLayout(layout)
        return top_bar

    def create_sidebar(self):
        """Create sidebar"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(12, 16, 12, 16)

        # Menu buttons
        self.menu_buttons = []

        menus = [
            ("🛒 Sotuv", 0, "F1"),
            ("📦 Mahsulotlar", 1, "F2"),
            ("👥 Mijozlar", 2, "F3"),
            ("📊 Hisobot", 3, "F4"),
            ("💰 Qarz To'lash", 4, "F5"),
            ("🏷️ Kategoriyalar", 5, "F6"),
            ("⚙️ Sozlamalar", 6, "F7"),
        ]

        for text, index, shortcut in menus:
            btn = QPushButton(text)
            btn.setObjectName("menuButton")
            btn.setToolTip(f"{text} ({shortcut})")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            layout.addWidget(btn)
            self.menu_buttons.append(btn)

        layout.addStretch()

        # Exit button
        exit_btn = QPushButton("🚪 Chiqish")
        exit_btn.setObjectName("btnDanger")
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)

        sidebar.setLayout(layout)
        return sidebar

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        ShortcutManager.setup_main_window_shortcuts(self)

    def setup_clock(self):
        """Setup live clock"""
        self.update_clock()
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second

    def update_clock(self):
        """Update clock display"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d.%m.%Y")
        self.clock_label.setText(f"🕐 {time_str} | 📅 {date_str}")

    def switch_page(self, index):
        """Switch page"""
        if self.content_stack.currentIndex() == index:
            return

        self.content_stack.setCurrentIndex(index)

        # Update button states
        for i, btn in enumerate(self.menu_buttons):
            if i == index:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # Refresh page
        current_page = self.content_stack.currentWidget()
        if hasattr(current_page, 'refresh'):
            current_page.refresh()
