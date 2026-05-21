# -*- coding: utf-8 -*-
"""
Glass Order Dialogs
Reusable dimension calculator widgets for window/glass sales.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utils.formatter import (
    calculate_window_metrics,
    format_decimal,
    format_meters,
    format_square_meters,
)
from widgets.custom_alert import CustomAlert


class WindowCalculationSummary(QWidget):
    """Reusable live summary card for window calculations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        panel = QFrame()
        panel.setStyleSheet(
            "QFrame {"
            "background-color: #0f1f2d;"
            "border: 1px solid #1f3a4f;"
            "border-radius: 12px;"
            "}"
        )

        panel_layout = QGridLayout()
        panel_layout.setContentsMargins(16, 14, 16, 14)
        panel_layout.setHorizontalSpacing(14)
        panel_layout.setVerticalSpacing(10)

        self.stock_label = QLabel()
        self.stock_label.setStyleSheet("color: #cbd5e1; font-size: 12px; font-weight: 600;")
        panel_layout.addWidget(self.stock_label, 0, 0, 1, 2)

        self.formula_label = QLabel()
        self.formula_label.setStyleSheet("color: #f8fafc; font-size: 15px; font-weight: 700;")
        panel_layout.addWidget(self.formula_label, 1, 0, 1, 2)

        kvm_title = QLabel("KVM")
        kvm_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 700;")
        panel_layout.addWidget(kvm_title, 2, 0)

        total_title = QLabel("JAMI")
        total_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 700;")
        panel_layout.addWidget(total_title, 2, 1)

        self.kvm_label = QLabel()
        self.kvm_label.setStyleSheet("color: #67e8f9; font-size: 18px; font-weight: 800;")
        panel_layout.addWidget(self.kvm_label, 3, 0)

        self.total_label = QLabel()
        self.total_label.setStyleSheet("color: #86efac; font-size: 18px; font-weight: 800;")
        panel_layout.addWidget(self.total_label, 3, 1)

        panel.setLayout(panel_layout)
        layout.addWidget(panel)
        self.setLayout(layout)

    def update_values(self, eni, boyi, narx_per_kvm, available_stock):
        metrics = calculate_window_metrics(eni, boyi, narx_per_kvm)
        self.stock_label.setText(f"Mavjud ombor: {format_square_meters(available_stock)}")
        self.formula_label.setText(
            f"{format_decimal(metrics['eni'])} x {format_decimal(metrics['boyi'])} = "
            f"{format_decimal(metrics['kvm'])} KVM"
        )
        self.kvm_label.setText(format_square_meters(metrics['kvm']))
        self.total_label.setText(f"{metrics['jami']:,.0f} so'm")


class GlassOrderDialog(QDialog):
    """Dimension-first add/edit dialog for glass cart items."""

    def __init__(self, parent, product, existing_item=None, available_stock=None):
        super().__init__(parent)
        self.product = product
        self.existing_item = existing_item
        self.available_stock = float(
            available_stock if available_stock is not None else getattr(product, "quantity", 0) or 0
        )
        self.setWindowTitle("Savatga qo'shish")
        self.setModal(True)
        self.setup_ui()
        self.setup_shortcuts()
        self.update_calculations()

    def setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.reject)
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.accept_if_valid)
        QShortcut(QKeySequence(Qt.Key_Enter), self).activated.connect(self.accept_if_valid)

    def setup_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        title = QLabel(self.product.name)
        title.setStyleSheet(
            "background-color: #102331; color: #f8fafc; font-size: 17px; "
            "font-weight: 700; padding: 14px 18px;"
        )
        root.addWidget(title)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        subtitle = QLabel("Eni va bo'yi kiriting. KVM va jami summa avtomatik hisoblanadi.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #475569; font-size: 12px; font-weight: 600;")
        layout.addWidget(subtitle)

        self.summary_card = WindowCalculationSummary(self)
        layout.addWidget(self.summary_card)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.eni_input = self.create_dimension_input()
        self.boyi_input = self.create_dimension_input()

        default_eni = 0.0
        default_boyi = 0.0
        if self.product.is_remnant:
            default_eni = float(self.product.eni or self.product.width or 0.01)
            default_boyi = float(self.product.boyi or self.product.height or 0.01)
            self.eni_input.setValue(default_eni)
            self.boyi_input.setValue(default_boyi)
            self.eni_input.setReadOnly(True)
            self.boyi_input.setReadOnly(True)
            self.eni_input.setButtonSymbols(QAbstractSpinBox.NoButtons)
            self.boyi_input.setButtonSymbols(QAbstractSpinBox.NoButtons)
        elif self.existing_item:
            default_eni = float(self.existing_item.get('eni', self.existing_item.get('width', 0.0)))
            default_boyi = float(self.existing_item.get('boyi', self.existing_item.get('height', 0.0)))
            self.eni_input.setValue(default_eni)
            self.boyi_input.setValue(default_boyi)
        else:
            self.eni_input.setValue(default_eni)
            self.boyi_input.setValue(default_boyi)

        self.eni_input.valueChanged.connect(self.update_calculations)
        self.boyi_input.valueChanged.connect(self.update_calculations)

        form.addRow("Eni (m):", self.eni_input)
        form.addRow("Bo'yi (m):", self.boyi_input)

        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999999)
        self.price_input.setMinimum(0)
        self.price_input.setDecimals(0)
        self.price_input.setGroupSeparatorShown(True)
        self.price_input.setSuffix(" so'm")
        self.price_input.setMinimumHeight(38)
        price_value = (
            self.existing_item.get('narx_per_kvm', self.existing_item.get('price'))
            if self.existing_item else
            (self.product.narx_per_kvm if self.product.narx_per_kvm is not None else self.product.selling_price)
        )
        self.price_input.setValue(float(price_value or 0))
        self.price_input.valueChanged.connect(self.update_calculations)
        form.addRow("Narx / KVM:", self.price_input)

        self.availability_label = QLabel()
        self.availability_label.setWordWrap(True)
        self.availability_label.setStyleSheet(
            "background-color: #e0f2fe; border: 1px solid #38bdf8; "
            "border-radius: 8px; padding: 10px 12px; color: #102331; font-weight: 600;"
        )
        form.addRow("Holat:", self.availability_label)

        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.setMinimumHeight(38)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        save_btn = QPushButton("Savatga qo'shish")
        save_btn.setObjectName("btnSuccess")
        save_btn.setMinimumHeight(38)
        save_btn.clicked.connect(self.accept_if_valid)
        buttons.addWidget(save_btn)

        layout.addLayout(buttons)
        root.addLayout(layout)
        self.setLayout(root)
        self.setFixedSize(500, 390)
        self.eni_input.setFocus()
        self.eni_input.selectAll()

    def create_dimension_input(self):
        spin = QDoubleSpinBox()
        spin.setDecimals(2)
        spin.setMaximum(9999)
        spin.setMinimum(0.0)          # 0.01 emas, 0.0 — foydalanuvchi o'zi kiriting
        spin.setSingleStep(0.05)
        spin.setSuffix(" m")
        spin.setMinimumHeight(38)
        spin.setSpecialValueText("—") # 0.0 bo'lganda "—" ko'rsatadi
        return spin

    def update_calculations(self):
        eni  = self.eni_input.value()
        boyi = self.boyi_input.value()
        price = max(self.price_input.value(), 0.01)

        if eni <= 0 or boyi <= 0:
            # Hali kiritilmagan — summary kartasini bo'sh ko'rsat
            self.summary_card.stock_label.setText(
                f"Mavjud ombor: {format_square_meters(self.available_stock)}"
            )
            self.summary_card.formula_label.setText("Eni va Bo'yini kiriting")
            self.summary_card.kvm_label.setText("0 kvm")
            self.summary_card.total_label.setText("0 so'm")
            self.availability_label.setText(
                f"Mavjud ombor: {format_square_meters(self.available_stock)}"
            )
            self.availability_label.setStyleSheet(
                "background-color: #e0f2fe; border: 1px solid #38bdf8; "
                "border-radius: 8px; padding: 10px 12px; color: #102331; font-weight: 600;"
            )
            return

        metrics = calculate_window_metrics(eni, boyi, price)
        self.summary_card.update_values(
            metrics['eni'], metrics['boyi'],
            metrics['narx_per_kvm'], self.available_stock,
        )

        if metrics['kvm'] > self.available_stock:
            self.availability_label.setText(
                "⚠ Kiritilgan o'lcham ombordagi kvm dan katta!"
            )
            self.availability_label.setStyleSheet(
                "background-color: #fef2f2; border: 1px solid #f87171; "
                "border-radius: 8px; padding: 10px 12px; color: #991b1b; font-weight: 700;"
            )
        else:
            self.availability_label.setText(
                f"✓ Sotuv: {format_square_meters(metrics['kvm'])}  |  "
                f"Qoladi: {format_square_meters(max(self.available_stock - metrics['kvm'], 0))}"
            )
            self.availability_label.setStyleSheet(
                "background-color: #ecfdf5; border: 1px solid #34d399; "
                "border-radius: 8px; padding: 10px 12px; color: #166534; font-weight: 700;"
            )

    def accept_if_valid(self):
        if self.eni_input.value() <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Eni kiritilmagan!")
            self.eni_input.setFocus()
            return
        if self.boyi_input.value() <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Bo'yi kiritilmagan!")
            self.boyi_input.setFocus()
            return
        if self.price_input.value() <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Narx/KVM kiritilmagan!")
            self.price_input.setFocus()
            return

        try:
            metrics = calculate_window_metrics(
                self.eni_input.value(),
                self.boyi_input.value(),
                self.price_input.value(),
            )
        except ValueError as exc:
            CustomAlert.show_warning(self, "Ogohlantirish", str(exc))
            return

        if metrics['kvm'] > self.available_stock:
            CustomAlert.show_warning(
                self, "Ogohlantirish",
                f"Omborda yetarli KVM yo'q!\n"
                f"So'ralgan: {metrics['kvm']:.4f} kvm\n"
                f"Mavjud: {self.available_stock:.4f} kvm"
            )
            return

        self.accept()

    def get_cart_item(self):
        metrics = calculate_window_metrics(
            self.eni_input.value(),
            self.boyi_input.value(),
            self.price_input.value(),
        )
        return {
            'product': self.product,
            'eni': metrics['eni'],
            'boyi': metrics['boyi'],
            'kvm': metrics['kvm'],
            'narx_per_kvm': metrics['narx_per_kvm'],
            'width': metrics['width'],
            'height': metrics['height'],
            'area_sqm': metrics['area_sqm'],
            'quantity': metrics['kvm'],
            'price': metrics['narx_per_kvm'],
            'jami': metrics['jami'],
        }
