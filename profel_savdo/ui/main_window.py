# -*- coding: utf-8 -*-
"""
Main Window - OYNA SAVDO
"""
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config.constants import APP_NAME, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_TITLE
from ui.pages.categories_page import CategoriesPage
from ui.pages.customers_page import CustomersPage
from ui.pages.debt_payment_page import DebtPaymentPage
from ui.pages.products_page import ProductsPage
from ui.pages.reports_page import ReportsPage
from ui.pages.sales_page import SalesPage
from ui.pages.settings_page import SettingsPage
from ui.shortcuts import ShortcutManager
from ui.theme import get_stylesheet
from utils.db_connection import get_db_connection
from widgets.custom_alert import CustomAlert


class MainWindow(QMainWindow):
    def __init__(self, cashier_name="Admin"):
        super().__init__()
        self.cashier_name = cashier_name
        self.db_conn = get_db_connection()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setStyleSheet(get_stylesheet())

        self.setup_ui()
        self.setup_shortcuts()
        self.setup_clock()

        self.content_stack.setCurrentIndex(0)
        self.switch_page(0)
        QTimer.singleShot(250, self.show_startup_database_notification)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.create_top_bar())

        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.create_sidebar())

        self.content_stack = QStackedWidget()
        self.sales_page = SalesPage(self.cashier_name)
        self.products_page = ProductsPage(self.cashier_name)
        self.customers_page = CustomersPage()
        self.reports_page = ReportsPage()
        self.debt_payment_page = DebtPaymentPage(self.cashier_name)
        self.categories_page = CategoriesPage()
        self.settings_page = SettingsPage()

        self.content_stack.addWidget(self.sales_page)
        self.content_stack.addWidget(self.products_page)
        self.content_stack.addWidget(self.customers_page)
        self.content_stack.addWidget(self.reports_page)
        self.content_stack.addWidget(self.debt_payment_page)
        self.content_stack.addWidget(self.categories_page)
        self.content_stack.addWidget(self.settings_page)
        content_layout.addWidget(self.content_stack)

        main_layout.addLayout(content_layout)
        central_widget.setLayout(main_layout)

    def create_top_bar(self):
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(60)

        layout = QHBoxLayout()
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        title_label = QLabel(APP_NAME)
        title_label.setObjectName("appTitle")
        layout.addWidget(title_label)
        layout.addStretch()

        self.clock_label = QLabel()
        self.clock_label.setObjectName("clockLabel")
        layout.addWidget(self.clock_label)

        user_label = QLabel(self.cashier_name)
        user_label.setObjectName("userLabel")
        layout.addWidget(user_label)

        shortcut_label = QLabel("F1-F7: Sahifalar | F8: Chek | F12: Savdo")
        shortcut_label.setObjectName("userLabel")
        layout.addWidget(shortcut_label)

        top_bar.setLayout(layout)
        return top_bar

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(12, 16, 12, 16)

        self.menu_buttons = []
        menus = [
            ("Sotuv", 0, "F1"),
            ("Oynalar", 1, "F2"),
            ("Mijozlar", 2, "F3"),
            ("Hisobot", 3, "F4"),
            ("Qarz To'lash", 4, "F5"),
            ("Kategoriyalar", 5, "F6"),
            ("Sozlamalar", 6, "F7"),
        ]

        for text, index, shortcut in menus:
            btn = QPushButton(text)
            btn.setObjectName("menuButton")
            btn.setToolTip(f"{text} ({shortcut})")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, idx=index: self.switch_page(idx))
            layout.addWidget(btn)
            self.menu_buttons.append(btn)

        layout.addStretch()

        exit_btn = QPushButton("Chiqish")
        exit_btn.setObjectName("btnDanger")
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)

        sidebar.setLayout(layout)
        return sidebar

    def setup_shortcuts(self):
        ShortcutManager.setup_main_window_shortcuts(self)

    def setup_clock(self):
        self.update_clock()
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

    def update_clock(self):
        now = datetime.now()
        self.clock_label.setText(f"{now.strftime('%H:%M:%S')} | {now.strftime('%d.%m.%Y')}")

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.menu_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        current_page = self.content_stack.currentWidget()
        if hasattr(current_page, 'refresh'):
            current_page.refresh()

    def show_startup_database_notification(self):
        warning_message = self.db_conn.get_fallback_warning_message()
        if warning_message:
            CustomAlert.show_warning(self, "PostgreSQL Ulanmadi", warning_message)
