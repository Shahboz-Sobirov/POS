# -*- coding: utf-8 -*-
"""
Customer Profile Dialog
Shows full customer history: sales, products, payments, debt
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QPushButton, QTabWidget, QWidget, QGroupBox)
from PySide6.QtCore import Qt
from services.customer_service import CustomerService
from utils.formatter import format_window_size


class CustomerProfileDialog(QDialog):
    """Full customer profile window"""
    def __init__(self, parent, customer):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle(f"Mijoz Profili - {customer.full_name}")
        self.setModal(True)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Customer info header
        header_group = QGroupBox("Mijoz Ma'lumotlari")
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        name_label = QLabel(f"👤 {self.customer.full_name}")
        name_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        header_layout.addWidget(name_label)

        phone_label = QLabel(f"📱 {self.customer.phone or 'Telefon kiritilmagan'}")
        phone_label.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(phone_label)

        debt_label = QLabel(f"💰 Qarz: {self.customer.total_debt:,.0f} so'm")
        debt_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {'red' if self.customer.total_debt > 0 else 'green'};")
        header_layout.addWidget(debt_label)

        header_group.setLayout(header_layout)
        layout.addWidget(header_group)

        # Tabs
        tabs = QTabWidget()

        # Sales tab
        sales_tab = self.create_sales_tab()
        tabs.addTab(sales_tab, "📊 Savdolar")

        # Debt payments tab
        payments_tab = self.create_payments_tab()
        tabs.addTab(payments_tab, "💳 To'lovlar")

        layout.addWidget(tabs)

        # Close button
        close_btn = QPushButton("Yopish")
        close_btn.setMinimumHeight(44)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)
        self.setMinimumSize(900, 600)

    def create_sales_tab(self):
        """Create sales history tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels([
            "Sana", "Oyna", "O'lcham", "To'lov", "Summa", "Foyda"
        ])
        self.sales_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.verticalHeader().setVisible(False)
        layout.addWidget(self.sales_table)

        widget.setLayout(layout)
        return widget

    def create_payments_tab(self):
        """Create debt payments tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Payments table
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(4)
        self.payments_table.setHorizontalHeaderLabels([
            "Sana", "Summa", "To'lov Turi", "Izoh"
        ])
        self.payments_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.payments_table.verticalHeader().setVisible(False)
        layout.addWidget(self.payments_table)

        widget.setLayout(layout)
        return widget

    def load_data(self):
        """Load customer data"""
        self.load_sales()
        self.load_payments()

    def load_sales(self):
        """Load sales history"""
        try:
            sales = CustomerService.get_customer_sales(self.customer.id)
            sale_rows = []
            for sale in sales:
                payment_str = self.format_payment_breakdown(sale.payment_breakdown)
                for item in sale.items:
                    if not item.product:
                        continue
                    sale_rows.append((sale, item, payment_str))

            self.sales_table.setRowCount(len(sale_rows))

            for row, (sale, item, payment_str) in enumerate(sale_rows):
                date_str = sale.sale_date.strftime("%d.%m.%Y %H:%M")
                self.sales_table.setItem(row, 0, QTableWidgetItem(date_str))
                self.sales_table.setItem(row, 1, QTableWidgetItem(item.product.name))
                self.sales_table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        format_window_size(
                            item.eni or item.width,
                            item.boyi or item.height,
                            item.kvm or item.area_sqm or item.quantity,
                        )
                    ),
                )
                self.sales_table.setItem(row, 3, QTableWidgetItem(payment_str))
                self.sales_table.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        f"{(item.kvm or item.area_sqm or item.quantity or 0) * (item.narx_per_kvm or item.price or 0):,.0f}"
                    ),
                )
                self.sales_table.setItem(row, 5, QTableWidgetItem(f"{item.profit:,.0f}"))

        except Exception as e:
            print(f"Error loading sales: {e}")

    def load_payments(self):
        """Load debt payments"""
        try:
            payments = CustomerService.get_customer_debt_payments(self.customer.id)
            self.payments_table.setRowCount(len(payments))

            for row, payment in enumerate(payments):
                # Date
                date_str = payment.payment_date.strftime("%d.%m.%Y %H:%M")
                self.payments_table.setItem(row, 0, QTableWidgetItem(date_str))

                # Amount
                self.payments_table.setItem(row, 1, QTableWidgetItem(f"{payment.amount:,.0f}"))

                # Payment type
                self.payments_table.setItem(row, 2, QTableWidgetItem(payment.payment_type))

                # Note
                self.payments_table.setItem(row, 3, QTableWidgetItem(payment.note or "-"))

        except Exception as e:
            print(f"Error loading payments: {e}")

    def format_payment_breakdown(self, breakdown):
        """Format payment breakdown"""
        if not breakdown:
            return "Naqd"

        parts = []
        if breakdown.get('naqd', 0) > 0:
            parts.append(f"Naqd: {breakdown['naqd']:,.0f}")
        if breakdown.get('karta', 0) > 0:
            parts.append(f"Karta: {breakdown['karta']:,.0f}")
        if breakdown.get('click', 0) > 0:
            parts.append(f"Click: {breakdown['click']:,.0f}")
        if breakdown.get('qarz', 0) > 0:
            parts.append(f"Qarz: {breakdown['qarz']:,.0f}")

        return "\n".join(parts) if parts else "Naqd"
