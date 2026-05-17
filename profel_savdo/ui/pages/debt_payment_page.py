# -*- coding: utf-8 -*-
"""
Debt Payment Page (F5)
Sorted by debt age (oldest first)
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QFormLayout, QComboBox,
                               QDoubleSpinBox, QTextEdit, QGroupBox)
from PySide6.QtCore import Qt
from services.customer_service import CustomerService
from services.debt_payment_service import DebtPaymentService
from widgets.custom_alert import CustomAlert
from utils.error_logger import log_exception, get_user_friendly_message


class DebtPaymentPage(QWidget):
    def __init__(self, cashier_name="Admin"):
        super().__init__()
        self.cashier_name = cashier_name
        self.current_customers = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Title
        title = QLabel("Qarz To'lash")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Info
        info_label = QLabel("⚠️ Qarzlar eskiligi bo'yicha tartiblangan (eng eski yuqorida)")
        info_label.setStyleSheet("color: #f39c12; font-size: 13px; font-weight: 500;")
        layout.addWidget(info_label)

        # Pay button
        pay_btn = QPushButton("💰 Qarz To'lash")
        pay_btn.setObjectName("btnSuccess")
        pay_btn.setMinimumHeight(44)
        pay_btn.setCursor(Qt.PointingHandCursor)
        pay_btn.clicked.connect(self.pay_debt)
        layout.addWidget(pay_btn)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Mijoz", "Telefon", "Qarz", "Eng Eski Savdo"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_customers_with_debt()

    def load_customers_with_debt(self):
        """Load customers with debt, sorted by oldest debt first"""
        try:
            customers = CustomerService.get_customers_with_debt_overview()
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
                debt_item.setBackground(Qt.red)
                debt_item.setForeground(Qt.white)
                self.table.setItem(row, 2, debt_item)

                # Oldest sale
                if customer_data['oldest_sale_date']:
                    oldest_date = customer_data['oldest_sale_date'].strftime("%d.%m.%Y")
                    self.table.setItem(row, 3, QTableWidgetItem(oldest_date))
                else:
                    self.table.setItem(row, 3, QTableWidgetItem("-"))

        except Exception as e:
            log_exception(e, "load_customers_with_debt")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def pay_debt(self):
        """Pay debt"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Mijoz tanlanmagan!")
            return

        row = selected[0].row()
        customer = self.current_customers[row]['customer']

        dialog = DebtPaymentDialog(self, customer, self.cashier_name)
        if dialog.exec() == QDialog.Accepted:
            self.load_customers_with_debt()

    def refresh(self):
        """Refresh page"""
        self.load_customers_with_debt()


class DebtPaymentDialog(QDialog):
    """Debt payment dialog with mixed payment support"""
    def __init__(self, parent, customer, cashier_name):
        super().__init__(parent)
        self.customer = customer
        self.cashier_name = cashier_name
        self.setWindowTitle(f"Qarz To'lash - {customer.full_name}")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Customer info
        info_group = QGroupBox("Mijoz Ma'lumotlari")
        info_layout = QVBoxLayout()

        name_label = QLabel(f"👤 {self.customer.full_name}")
        name_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        info_layout.addWidget(name_label)

        debt_label = QLabel(f"💰 Qarz: {self.customer.total_debt:,.0f} so'm")
        debt_label.setStyleSheet("font-size: 18px; font-weight: 600; color: red;")
        info_layout.addWidget(debt_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Payment inputs
        payment_group = QGroupBox("To'lov")
        payment_layout = QVBoxLayout()
        payment_layout.setSpacing(12)

        # Naqd
        naqd_layout = QHBoxLayout()
        naqd_label = QLabel("💵 Naqd:")
        naqd_label.setFixedWidth(80)
        self.naqd_input = QDoubleSpinBox()
        self.naqd_input.setMaximum(999999999)
        self.naqd_input.setMinimumHeight(40)
        self.naqd_input.setSuffix(" so'm")
        self.naqd_input.valueChanged.connect(self.update_total)
        naqd_layout.addWidget(naqd_label)
        naqd_layout.addWidget(self.naqd_input)
        payment_layout.addLayout(naqd_layout)

        # Karta
        karta_layout = QHBoxLayout()
        karta_label = QLabel("💳 Karta:")
        karta_label.setFixedWidth(80)
        self.karta_input = QDoubleSpinBox()
        self.karta_input.setMaximum(999999999)
        self.karta_input.setMinimumHeight(40)
        self.karta_input.setSuffix(" so'm")
        self.karta_input.valueChanged.connect(self.update_total)
        karta_layout.addWidget(karta_label)
        karta_layout.addWidget(self.karta_input)
        payment_layout.addLayout(karta_layout)

        # Click
        click_layout = QHBoxLayout()
        click_label = QLabel("📱 Click:")
        click_label.setFixedWidth(80)
        self.click_input = QDoubleSpinBox()
        self.click_input.setMaximum(999999999)
        self.click_input.setMinimumHeight(40)
        self.click_input.setSuffix(" so'm")
        self.click_input.valueChanged.connect(self.update_total)
        click_layout.addWidget(click_label)
        click_layout.addWidget(self.click_input)
        payment_layout.addLayout(click_layout)

        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)

        # Total
        self.total_label = QLabel("Jami: 0 so'm")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: 600; color: #27ae60; padding: 12px;")
        self.total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.total_label)

        # Note
        note_label = QLabel("Izoh:")
        layout.addWidget(note_label)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(80)
        layout.addWidget(self.note_input)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        pay_btn = QPushButton("To'lash")
        pay_btn.setObjectName("btnSuccess")
        pay_btn.setMinimumHeight(44)
        pay_btn.setCursor(Qt.PointingHandCursor)
        pay_btn.clicked.connect(self.process_payment)
        btn_layout.addWidget(pay_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setFixedSize(500, 600)

    def update_total(self):
        """Update total payment"""
        total = self.naqd_input.value() + self.karta_input.value() + self.click_input.value()
        self.total_label.setText(f"Jami: {total:,.0f} so'm")

    def process_payment(self):
        """Process payment"""
        naqd = self.naqd_input.value()
        karta = self.karta_input.value()
        click = self.click_input.value()
        total = naqd + karta + click

        if total <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "To'lov summasi 0 dan katta bo'lishi kerak!")
            return

        if total > self.customer.total_debt:
            if not CustomAlert.show_confirm(
                self, "Ogohlantirish",
                f"To'lov summasi qarzdan ko'p!\n\nQarz: {self.customer.total_debt:,.0f} so'm\nTo'lov: {total:,.0f} so'm\n\nDavom ettirilsinmi?"
            ):
                return

        # Determine payment type
        payment_breakdown = {}
        if naqd > 0:
            payment_breakdown['naqd'] = naqd
        if karta > 0:
            payment_breakdown['karta'] = karta
        if click > 0:
            payment_breakdown['click'] = click

        if len(payment_breakdown) > 1:
            payment_type = "Mixed"
        elif naqd > 0:
            payment_type = "Naqd"
        elif karta > 0:
            payment_type = "Karta"
        else:
            payment_type = "Click"

        try:
            DebtPaymentService.create_payment(
                customer_id=self.customer.id,
                amount=total,
                payment_type=payment_type,
                payment_breakdown=payment_breakdown,
                note=self.note_input.toPlainText() or None,
                cashier=self.cashier_name
            )

            CustomAlert.show_success(self, "Muvaffaqiyat", f"To'lov qabul qilindi!\n\nSumma: {total:,.0f} so'm")
            self.accept()

        except Exception as e:
            log_exception(e, "process_debt_payment")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))
