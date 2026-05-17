# -*- coding: utf-8 -*-
"""
Customers Page (F3)
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QDialog, QFormLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from services.customer_service import CustomerService
from ui.dialogs.customer_profile_dialog import CustomerProfileDialog
from widgets.custom_alert import CustomAlert
from utils.error_logger import log_exception, get_user_friendly_message


class CustomersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.current_customers = []
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Title
        title = QLabel("Mijozlar")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Search and buttons
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Mijoz qidirish...")
        self.search_input.setMinimumHeight(44)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.on_search_changed)
        top_layout.addWidget(self.search_input, 2)

        add_btn = QPushButton("➕ Yangi Mijoz")
        add_btn.setObjectName("btnSuccess")
        add_btn.setMinimumHeight(44)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_customer)
        top_layout.addWidget(add_btn)

        edit_btn = QPushButton("✏️ Tahrirlash")
        edit_btn.setMinimumHeight(44)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self.edit_customer)
        top_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ O'chirish")
        delete_btn.setObjectName("btnDanger")
        delete_btn.setMinimumHeight(44)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self.delete_customer)
        top_layout.addWidget(delete_btn)

        layout.addLayout(top_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Ism Familya", "Telefon", "Qarz", "Oxirgi Savdo", "Jami Savdo"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.doubleClicked.connect(self.show_customer_profile)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_customers()

    def setup_shortcuts(self):
        """Setup shortcuts"""
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(
            lambda: self.search_input.setFocus()
        )

    def on_search_changed(self):
        """Search input changed"""
        self.search_timer.stop()
        self.search_timer.start(300)

    def perform_search(self):
        """Perform search"""
        query = self.search_input.text().strip()
        try:
            customers = CustomerService.get_customer_overview(query or None)
            self.populate_table(customers)
        except Exception as e:
            log_exception(e, "search_customers")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def load_customers(self):
        """Load all customers"""
        try:
            customers = CustomerService.get_customer_overview()
            self.populate_table(customers)
        except Exception as e:
            log_exception(e, "load_customers")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def populate_table(self, customers):
        """Populate table"""
        self.current_customers = customers
        self.table.setRowCount(len(customers))

        for row, customer_data in enumerate(customers):
            customer = customer_data['customer']

            # Name
            self.table.setItem(row, 0, QTableWidgetItem(customer.full_name))

            # Phone
            self.table.setItem(row, 1, QTableWidgetItem(customer.phone or "-"))

            # Debt
            debt_item = QTableWidgetItem(f"{customer.total_debt:,.0f} so'm")
            if customer.total_debt > 0:
                debt_item.setBackground(Qt.red)
                debt_item.setForeground(Qt.white)
            self.table.setItem(row, 2, debt_item)

            # Last sale
            if customer_data['last_sale_date']:
                last_sale_date = customer_data['last_sale_date'].strftime("%d.%m.%Y")
                self.table.setItem(row, 3, QTableWidgetItem(last_sale_date))
            else:
                self.table.setItem(row, 3, QTableWidgetItem("-"))

            # Total sales
            self.table.setItem(row, 4, QTableWidgetItem(str(customer_data['total_sales'])))

    def add_customer(self):
        """Add customer"""
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                CustomerService.create(
                    full_name=dialog.name_input.text(),
                    phone=dialog.phone_input.text() or None
                )
                self.load_customers()
                CustomAlert.show_success(self, "Muvaffaqiyat", "Mijoz qo'shildi!")
            except Exception as e:
                log_exception(e, "add_customer")
                CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def edit_customer(self):
        """Edit customer"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Mijoz tanlanmagan!")
            return

        row = selected[0].row()
        customer = self.current_customers[row]['customer']

        dialog = CustomerDialog(self, customer)
        if dialog.exec() == QDialog.Accepted:
            try:
                CustomerService.update(
                    customer.id,
                    full_name=dialog.name_input.text(),
                    phone=dialog.phone_input.text() or None
                )
                self.load_customers()
                CustomAlert.show_success(self, "Muvaffaqiyat", "Mijoz tahrirlandi!")
            except Exception as e:
                log_exception(e, "edit_customer")
                CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def delete_customer(self):
        """Delete customer"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Mijoz tanlanmagan!")
            return

        if CustomAlert.show_confirm(self, "Tasdiqlash", "Mijozni o'chirishni xohlaysizmi?"):
            row = selected[0].row()
            customer = self.current_customers[row]['customer']

            try:
                CustomerService.delete(customer.id)
                self.load_customers()
                CustomAlert.show_success(self, "Muvaffaqiyat", "Mijoz o'chirildi!")
            except Exception as e:
                log_exception(e, "delete_customer")
                CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def show_customer_profile(self):
        """Show customer profile (double-click)"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return

        row = selected[0].row()
        customer = self.current_customers[row]['customer']

        dialog = CustomerProfileDialog(self, customer)
        dialog.exec()

    def refresh(self):
        """Refresh page"""
        self.load_customers()


class CustomerDialog(QDialog):
    """Customer CRUD dialog"""
    def __init__(self, parent, customer=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Yangi Mijoz" if not customer else "Mijozni Tahrirlash")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(40)
        if self.customer:
            self.name_input.setText(self.customer.full_name)
        layout.addRow("Ism Familya:", self.name_input)

        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(40)
        self.phone_input.setPlaceholderText("+998 90 123 45 67")
        if self.customer:
            self.phone_input.setText(self.customer.phone or "")
        layout.addRow("Telefon:", self.phone_input)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Saqlash")
        save_btn.setObjectName("btnSuccess")
        save_btn.setMinimumHeight(44)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)

        layout.addRow("", btn_layout)

        self.setLayout(layout)
        self.setFixedSize(450, 250)
