# -*- coding: utf-8 -*-
"""
Quantity Edit Dialog - Compact POS Style
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QDoubleSpinBox, QLineEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence


class QuantityEditDialog(QDialog):
    """Compact quantity edit dialog for cart items"""

    def __init__(self, parent, product_name, current_quantity, unit):
        super().__init__(parent)
        self.product_name = product_name
        self.current_quantity = current_quantity
        self.unit = unit
        self.new_quantity = current_quantity

        self.setWindowTitle("Miqdor Tahrirlash")
        self.setModal(True)
        self.setFixedWidth(400)

        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        """Setup compact UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Title
        title_label = QLabel("Miqdor Tahrirlash")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #102331;
                padding: 4px 0;
            }
        """)
        layout.addWidget(title_label)

        # Product name (readonly)
        product_label = QLabel("Mahsulot:")
        product_label.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 600;")
        layout.addWidget(product_label)

        product_value = QLineEdit(self.product_name)
        product_value.setReadOnly(True)
        product_value.setStyleSheet("""
            QLineEdit {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                color: #475569;
            }
        """)
        layout.addWidget(product_value)

        # Current quantity (readonly)
        current_label = QLabel("Hozirgi miqdor:")
        current_label.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 600;")
        layout.addWidget(current_label)

        current_value = QLineEdit(f"{self.current_quantity:,.2f} {self.unit}")
        current_value.setReadOnly(True)
        current_value.setStyleSheet("""
            QLineEdit {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                color: #475569;
            }
        """)
        layout.addWidget(current_value)

        # New quantity input
        new_label = QLabel("Yangi miqdor:")
        new_label.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 600;")
        layout.addWidget(new_label)

        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setMaximum(999999)
        self.quantity_input.setValue(self.current_quantity)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setSuffix(f" {self.unit}")
        self.quantity_input.setMinimumHeight(36)
        self.quantity_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                border: 2px solid #38bdf8;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
                font-weight: 600;
                color: #0f172a;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #0284c7;
                background-color: #f0f9ff;
            }
        """)
        self.quantity_input.selectAll()
        self.quantity_input.setFocus()
        layout.addWidget(self.quantity_input)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        cancel_btn = QPushButton("Bekor qilish (Esc)")
        cancel_btn.setMinimumHeight(36)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                border-color: #94a3b8;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("✓ Saqlash (Enter)")
        save_btn.setMinimumHeight(36)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        save_btn.clicked.connect(self.save_quantity)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence("Return"), self).activated.connect(self.save_quantity)
        QShortcut(QKeySequence("Enter"), self).activated.connect(self.save_quantity)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.reject)

    def save_quantity(self):
        """Save new quantity"""
        self.new_quantity = self.quantity_input.value()
        self.accept()

    def get_quantity(self):
        """Get new quantity"""
        return self.new_quantity
