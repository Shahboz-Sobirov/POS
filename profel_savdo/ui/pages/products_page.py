# -*- coding: utf-8 -*-
"""
Products Page (F2)
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QHeaderView,
    QVBoxLayout,
    QWidget,
)

from services.audit_service import AuditService
from services.category_service import CategoryService
from services.product_service import ProductService
from utils.error_logger import get_user_friendly_message, log_exception
from utils.formatter import format_quantity_display
from widgets.custom_alert import CustomAlert


class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.current_products = []
        self.view_mode = "glass"
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Oynalar Ombori")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        summary_layout = QHBoxLayout()
        self.total_products_label = QLabel()
        self.total_products_label.setStyleSheet(self.summary_style("#eff6ff", "#1e3a8a", "#bfdbfe"))
        summary_layout.addWidget(self.total_products_label)

        self.total_inventory_value_label = QLabel()
        self.total_inventory_value_label.setStyleSheet(self.summary_style("#ecfdf5", "#166534", "#bbf7d0"))
        summary_layout.addWidget(self.total_inventory_value_label)
        summary_layout.addStretch()
        layout.addLayout(summary_layout)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Oyna qidirish...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.on_search_changed)
        top_layout.addWidget(self.search_input, 2)

        self.glass_btn = QPushButton("Asosiy oynalar")
        self.glass_btn.setCheckable(True)
        self.glass_btn.setChecked(True)
        self.glass_btn.clicked.connect(lambda: self.set_view_mode("glass"))
        top_layout.addWidget(self.glass_btn)

        self.remnant_btn = QPushButton("Qoldiq oynalar")
        self.remnant_btn.setCheckable(True)
        self.remnant_btn.clicked.connect(lambda: self.set_view_mode("remnant"))
        top_layout.addWidget(self.remnant_btn)

        self.add_btn = QPushButton("Yangi oyna")
        self.add_btn.setObjectName("btnSuccess")
        self.add_btn.setMinimumHeight(40)
        self.add_btn.clicked.connect(self.add_product)
        top_layout.addWidget(self.add_btn)

        edit_btn = QPushButton("Tahrirlash")
        edit_btn.setMinimumHeight(40)
        edit_btn.clicked.connect(self.edit_product)
        top_layout.addWidget(edit_btn)

        delete_btn = QPushButton("O'chirish")
        delete_btn.setObjectName("btnDanger")
        delete_btn.setMinimumHeight(40)
        delete_btn.clicked.connect(self.delete_product)
        top_layout.addWidget(delete_btn)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Oyna", "Kategoriya", "Narx/KVM", "Kelgan narx", "Ombor", "Birlik", "Eslatma"]
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.setWordWrap(False)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_products()

    def summary_style(self, bg, fg, border):
        return (
            "QLabel {"
            f"background-color: {bg}; color: {fg}; border: 1px solid {border};"
            "border-radius: 10px; padding: 10px 14px; font-size: 14px; font-weight: 700; }"
        )

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(
            lambda: self.search_input.setFocus()
        )

    def set_view_mode(self, mode):
        self.view_mode = mode
        self.glass_btn.setChecked(mode == "glass")
        self.remnant_btn.setChecked(mode == "remnant")
        self.add_btn.setText("Yangi oyna" if mode == "glass" else "Yangi qoldiq")
        self.load_products()

    def on_search_changed(self):
        self.search_timer.stop()
        self.search_timer.start(300)

    def perform_search(self):
        self.load_products()

    def load_products(self):
        try:
            query = self.search_input.text().strip()
            products = ProductService.search(query) if query else ProductService.get_all()
            if self.view_mode == "glass":
                products = [product for product in products if not product.is_remnant]
            else:
                products = [product for product in products if product.is_remnant]
            self.populate_table(products)
        except Exception as e:
            log_exception(e, "load_products")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def populate_table(self, products):
        self.current_products = list(products)
        self.update_summary(products)
        self.table.setRowCount(len(products))

        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(product.name))
            cat_name = product.category.name if product.category else "-"
            self.table.setItem(row, 1, QTableWidgetItem(cat_name))
            price_value = product.narx_per_kvm if product.narx_per_kvm is not None else product.selling_price
            self.table.setItem(row, 2, QTableWidgetItem(f"{price_value:,.0f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{product.cost_price:,.0f}"))
            stock_item = QTableWidgetItem(format_quantity_display(product.quantity or 0, product.unit or "kvm"))
            if product.quantity <= 0:
                stock_item.setBackground(Qt.red)
                stock_item.setForeground(Qt.white)
            elif product.quantity <= 1:
                stock_item.setBackground(Qt.yellow)
            self.table.setItem(row, 4, stock_item)
            self.table.setItem(row, 5, QTableWidgetItem((product.unit or "kvm").upper()))
            self.table.setItem(row, 6, QTableWidgetItem(product.note or "-"))
            for col in range(1, 6):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
        self.table.resizeRowsToContents()

    def update_summary(self, products):
        total_products = len(products)
        total_inventory_value = sum(float(product.quantity or 0) * float(product.selling_price or 0) for product in products)
        summary_name = "Asosiy oynalar" if self.view_mode == "glass" else "Qoldiq oynalar"
        self.total_products_label.setText(f"{summary_name}: {total_products} ta")
        self.total_inventory_value_label.setText(f"Umumiy qiymat: {total_inventory_value:,.0f} UZS")

    def add_product(self):
        dialog = ProductDialog(self, product_type=self.view_mode)
        if dialog.exec() != QDialog.Accepted:
            return

        try:
            data = dialog.get_data()
            ProductService.create(**data)
            self.load_products()
            CustomAlert.show_success(self, "Muvaffaqiyat", "Ma'lumot saqlandi!")
        except Exception as e:
            log_exception(e, "add_product")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def edit_product(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Oyna tanlanmagan!")
            return

        row = selected[0].row()
        if row >= len(self.current_products):
            return

        product = self.current_products[row]
        dialog = ProductDialog(
            self,
            product=product,
            product_type="remnant" if product.is_remnant else "glass",
        )
        if dialog.exec() != QDialog.Accepted:
            return

        try:
            data = dialog.get_data()
            ProductService.update(product.id, **data)
            AuditService.log_product_edited("Admin", product.id, product.name, {"action": "edited"})
            self.load_products()
            CustomAlert.show_success(self, "Muvaffaqiyat", "Ma'lumot yangilandi!")
        except Exception as e:
            log_exception(e, "edit_product")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def delete_product(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Oyna tanlanmagan!")
            return

        row = selected[0].row()
        if row >= len(self.current_products):
            return

        product = self.current_products[row]
        text = "Tanlangan qoldiq oynani o'chirishni xohlaysizmi?" if product.is_remnant else "Tanlangan oynani o'chirishni xohlaysizmi?"
        if not CustomAlert.show_confirm(self, "Tasdiqlash", text):
            return

        try:
            ProductService.delete(product.id)
            AuditService.log_product_deleted("Admin", product.id, product.name)
            self.load_products()
            CustomAlert.show_success(self, "Muvaffaqiyat", "Ma'lumot o'chirildi!")
        except Exception as e:
            log_exception(e, "delete_product")
            CustomAlert.show_error(self, "Xato", str(e) if isinstance(e, ValueError) else get_user_friendly_message(e))

    def refresh(self):
        self.load_products()


class ProductDialog(QDialog):
    """Professional glass inventory dialog."""

    def __init__(self, parent, product=None, product_type="glass"):
        super().__init__(parent)
        self.product = product
        self.product_type = product_type
        self.setWindowTitle("Oyna ma'lumoti")
        self.setModal(True)
        self.setup_ui()
        self.setup_shortcuts()
        self.name_input.setFocus()
        self.name_input.selectAll()

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Return"), self).activated.connect(self.save)
        QShortcut(QKeySequence("Enter"), self).activated.connect(self.save)
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.reject)

    def setup_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QLabel("Oyna ma'lumoti")
        header.setStyleSheet(
            "background-color: #102331; color: #f8fafc; font-size: 17px; "
            "font-weight: 700; padding: 14px 18px;"
        )
        root.addWidget(header)

        body = QVBoxLayout()
        body.setContentsMargins(22, 20, 22, 18)
        body.setSpacing(14)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(38)
        self.name_input.setPlaceholderText("Oyna nomi")
        if self.product:
            self.name_input.setText(self.product.name)
        form.addRow("Oyna nomi:", self.name_input)

        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(38)
        self.category_combo.addItem("Kategoriyasiz", None)
        for category in CategoryService.get_all():
            self.category_combo.addItem(category.name, category.id)
        if self.product and self.product.category_id:
            index = self.category_combo.findData(self.product.category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        form.addRow("Kategoriya:", self.category_combo)

        self.selling_price_input = self.create_money_input()
        selling_price = self.product.narx_per_kvm if self.product and self.product.narx_per_kvm is not None else (
            self.product.selling_price if self.product else 0
        )
        self.selling_price_input.setValue(float(selling_price or 0))
        form.addRow("Sotuv narxi / KVM:", self.selling_price_input)

        self.cost_price_input = self.create_money_input()
        self.cost_price_input.setValue(float(self.product.cost_price) if self.product else 0)
        form.addRow("Kelgan narx / KVM:", self.cost_price_input)

        stock_layout = QHBoxLayout()
        stock_layout.setSpacing(8)
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setDecimals(2)
        self.quantity_input.setMaximum(999999999)
        self.quantity_input.setGroupSeparatorShown(True)
        self.quantity_input.setMinimumHeight(38)
        self.quantity_input.setValue(float(self.product.quantity) if self.product else 0)
        stock_layout.addWidget(self.quantity_input, 3)

        self.unit_combo = QComboBox()
        self.unit_combo.setMinimumHeight(38)
        self.unit_combo.addItem("KVM", "kvm")
        self.unit_combo.addItem("Dona", "dona")
        existing_unit = (self.product.unit if self.product else "kvm") or "kvm"
        unit_index = self.unit_combo.findData(existing_unit)
        if unit_index < 0:
            self.unit_combo.addItem(existing_unit, existing_unit)
            unit_index = self.unit_combo.findData(existing_unit)
        self.unit_combo.setCurrentIndex(unit_index)
        stock_layout.addWidget(self.unit_combo, 1)

        form.addRow("Ombor:", stock_layout)

        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(74)
        self.note_input.setPlaceholderText("Eslatma")
        if self.product and self.product.note:
            self.note_input.setPlainText(self.product.note)
        form.addRow("Eslatma:", self.note_input)

        body.addLayout(form)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(38)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setObjectName("btnSuccess")
        save_btn.setMinimumHeight(38)
        save_btn.clicked.connect(self.save)
        buttons.addWidget(save_btn)

        body.addLayout(buttons)
        root.addLayout(body)
        self.setLayout(root)
        self.setFixedSize(540, 430)

    def create_money_input(self):
        spin = QDoubleSpinBox()
        spin.setMaximum(999999999)
        spin.setDecimals(0)
        spin.setGroupSeparatorShown(True)
        spin.setSuffix(" so'm")
        spin.setMinimumHeight(38)
        return spin

    def save(self):
        if not self.name_input.text().strip():
            CustomAlert.show_warning(self, "Ogohlantirish", "Oyna nomi kiritilmagan!")
            self.name_input.setFocus()
            return
        if self.selling_price_input.value() <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Sotuv narxi 0 dan katta bo'lishi kerak!")
            self.selling_price_input.setFocus()
            return
        if self.cost_price_input.value() < 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Kelgan narx manfiy bo'lishi mumkin emas!")
            self.cost_price_input.setFocus()
            return
        if self.quantity_input.value() < 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Ombor manfiy bo'lishi mumkin emas!")
            self.quantity_input.setFocus()
            return
        self.accept()

    def get_data(self):
        preserved_width = None
        preserved_height = None
        preserved_area = None
        if self.product:
            preserved_width = self.product.eni if self.product.eni is not None else self.product.width
            preserved_height = self.product.boyi if self.product.boyi is not None else self.product.height
            preserved_area = self.product.kvm if self.product.kvm is not None else self.product.area_sqm

        narx_per_kvm = self.selling_price_input.value()
        return {
            'name': self.name_input.text().strip(),
            'category_id': self.category_combo.currentData(),
            'selling_price': narx_per_kvm,
            'narx_per_kvm': narx_per_kvm,
            'cost_price': self.cost_price_input.value(),
            'quantity': self.quantity_input.value(),
            'unit': self.unit_combo.currentData(),
            'barcode': None,
            'product_type': self.product_type,
            'eni': preserved_width,
            'boyi': preserved_height,
            'kvm': preserved_area,
            'width': preserved_width,
            'height': preserved_height,
            'area_sqm': preserved_area,
            'note': self.note_input.toPlainText().strip() or None,
        }
