# -*- coding: utf-8 -*-
"""
Products Page (F2)
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QDialog, QFormLayout,
                               QComboBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from services.product_service import ProductService
from services.category_service import CategoryService
from services.audit_service import AuditService
from ui.dialogs.error_dialog import show_error
from utils.logger import logger
from widgets.custom_alert import CustomAlert
from utils.error_logger import log_exception, get_user_friendly_message


class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()
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
        title = QLabel("Mahsulotlar")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Search and buttons
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Mahsulot qidirish...")
        self.search_input.setMinimumHeight(44)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.on_search_changed)
        top_layout.addWidget(self.search_input, 2)

        add_btn = QPushButton("➕ Yangi Mahsulot")
        add_btn.setObjectName("btnSuccess")
        add_btn.setMinimumHeight(44)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_product)
        top_layout.addWidget(add_btn)

        edit_btn = QPushButton("✏️ Tahrirlash")
        edit_btn.setMinimumHeight(44)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self.edit_product)
        top_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ O'chirish")
        delete_btn.setObjectName("btnDanger")
        delete_btn.setMinimumHeight(44)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self.delete_product)
        top_layout.addWidget(delete_btn)

        layout.addLayout(top_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Nomi", "Kategoriya", "Sotuv Narxi", "Kelgan Narx",
            "Ombor", "Birlik"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_products()

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
        if query:
            try:
                products = ProductService.search(query)
                self.populate_table(products)
            except Exception as e:
                logger.log_error("Mahsulotlar", "Mahsulot qidirish", e)
                show_error(
                    self,
                    "Qidirishda xato",
                    "Mahsulotlarni qidirishda xato yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                    e
                )
        else:
            self.load_products()

    def load_products(self):
        """Load all products"""
        try:
            products = ProductService.get_all()
            self.populate_table(products)
        except Exception as e:
            logger.log_error("Mahsulotlar", "Mahsulotlarni yuklash", e)
            show_error(
                self,
                "Yuklashda xato",
                "Mahsulotlarni yuklashda xato yuz berdi. Iltimos, dasturni qayta ishga tushiring.",
                e
            )

    def populate_table(self, products):
        """Populate table"""
        self.table.setRowCount(len(products))

        for row, product in enumerate(products):
            # Name
            self.table.setItem(row, 0, QTableWidgetItem(product.name))

            # Category
            cat_name = product.category.name if product.category else "-"
            self.table.setItem(row, 1, QTableWidgetItem(cat_name))

            # Selling price
            self.table.setItem(row, 2, QTableWidgetItem(f"{product.selling_price:,.0f}"))

            # Cost price
            self.table.setItem(row, 3, QTableWidgetItem(f"{product.cost_price:,.0f}"))

            # Stock
            stock_item = QTableWidgetItem(f"{product.quantity:,.2f}")
            if product.quantity <= 0:
                stock_item.setBackground(Qt.red)
                stock_item.setForeground(Qt.white)
            elif product.quantity <= 5:
                stock_item.setBackground(Qt.yellow)
            self.table.setItem(row, 4, stock_item)

            # Unit
            self.table.setItem(row, 5, QTableWidgetItem(product.unit))

    def add_product(self):
        """Add product"""
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                # Validation
                name = dialog.name_input.text().strip()
                if not name:
                    show_error(
                        self,
                        "Validatsiya xatosi",
                        "Mahsulot nomi bo'sh bo'lishi mumkin emas.",
                        None
                    )
                    return

                category_id = dialog.category_combo.currentData()
                selling_price = dialog.selling_price_input.value()
                cost_price = dialog.cost_price_input.value()
                quantity = dialog.quantity_input.value()
                unit = dialog.unit_input.text().strip()

                if selling_price <= 0:
                    show_error(
                        self,
                        "Validatsiya xatosi",
                        "Sotuv narxi 0 dan katta bo'lishi kerak.",
                        None
                    )
                    return

                if cost_price < 0:
                    show_error(
                        self,
                        "Validatsiya xatosi",
                        "Kelgan narx manfiy bo'lishi mumkin emas.",
                        None
                    )
                    return

                if quantity < 0:
                    show_error(
                        self,
                        "Validatsiya xatosi",
                        "Ombor soni manfiy bo'lishi mumkin emas.",
                        None
                    )
                    return

                if not unit:
                    show_error(
                        self,
                        "Validatsiya xatosi",
                        "Birlik bo'sh bo'lishi mumkin emas.",
                        None
                    )
                    return

                ProductService.create(
                    name=name,
                    category_id=category_id,
                    selling_price=selling_price,
                    cost_price=cost_price,
                    quantity=quantity,
                    unit=unit,
                    barcode=None
                )
                self.load_products()
                CustomAlert.show_success(self, "Muvaffaqiyat", "Mahsulot qo'shildi!")
            except Exception as e:
                log_exception(e, "add_product")
                CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def edit_product(self):
        """Edit product"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Mahsulot tanlanmagan!")
            return

        row = selected[0].row()
        products = ProductService.get_all()
        product = products[row]

        dialog = ProductDialog(self, product)
        if dialog.exec() == QDialog.Accepted:
            try:
                # Validation
                name = dialog.name_input.text().strip()
                if not name:
                    show_error(
                        self,
                        "Validatsiya xatosi",
                        "Mahsulot nomi bo'sh bo'lishi mumkin emas.",
                        None
                    )
                    return

                category_id = dialog.category_combo.currentData()
                selling_price = dialog.selling_price_input.value()
                cost_price = dialog.cost_price_input.value()
                quantity = dialog.quantity_input.value()
                unit = dialog.unit_input.text().strip()

                if selling_price <= 0:
                    show_error(
                        self,
                        "Validatsiya xatosi",
                        "Sotuv narxi 0 dan katta bo'lishi kerak.",
                        None
                    )
                    return

                if cost_price < 0:
                    show_error(
                        self,
                        "Validatsiya xatosi",
                        "Kelgan narx manfiy bo'lishi mumkin emas.",
                        None
                    )
                    return

                if quantity < 0:
                    show_error(
                        self,
                        "Validatsiya xatosi",
                        "Ombor soni manfiy bo'lishi mumkin emas.",
                        None
                    )
                    return

                if not unit:
                    show_error(
                        self,
                        "Validatsiya xatosi",
                        "Birlik bo'sh bo'lishi mumkin emas.",
                        None
                    )
                    return

                ProductService.update(
                    product.id,
                    name=name,
                    category_id=category_id,
                    selling_price=selling_price,
                    cost_price=cost_price,
                    quantity=quantity,
                    unit=unit,
                    barcode=None
                )

                # Audit log
                AuditService.log_product_edited(
                    "Admin",
                    product.id,
                    product.name,
                    {"action": "edited"}
                )

                self.load_products()
                CustomAlert.show_success(self, "Muvaffaqiyat", "Mahsulot tahrirlandi!")
            except Exception as e:
                log_exception(e, "edit_product")
                CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def delete_product(self):
        """Delete product"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Mahsulot tanlanmagan!")
            return

        if not CustomAlert.show_confirm(
            self, "Tasdiqlash",
            "Mahsulotni o'chirishni xohlaysizmi?"
        ):
            return

        row = selected[0].row()
        products = ProductService.get_all()
        product = products[row]

        try:
            ProductService.delete(product.id)

            # Audit log
            AuditService.log_product_deleted("Admin", product.id, product.name)

            self.load_products()
            CustomAlert.show_success(self, "Muvaffaqiyat", "Mahsulot o'chirildi!")
        except Exception as e:
            log_exception(e, "delete_product")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def refresh(self):
        """Refresh page"""
        self.load_products()


class ProductDialog(QDialog):
    """Product CRUD dialog - Modern Warehouse ERP Style"""
    def __init__(self, parent, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Yangi Mahsulot" if not product else "Mahsulotni Tahrirlash")
        self.setModal(True)
        self.setFixedWidth(720)
        self.setup_ui()
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        from PySide6.QtGui import QShortcut, QKeySequence

        # Enter to save
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.accept)
        QShortcut(QKeySequence(Qt.Key_Enter), self).activated.connect(self.accept)

        # Esc to cancel
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.reject)

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QLabel("📦 " + ("Yangi Mahsulot" if not self.product else "Mahsulotni Tahrirlash"))
        header.setStyleSheet("""
            QLabel {
                background-color: #102331;
                color: #f8fafc;
                font-size: 16px;
                font-weight: 600;
                padding: 20px 28px;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }
        """)
        main_layout.addWidget(header)

        # Form container
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background-color: #13293a;
            }
        """)
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(28, 28, 28, 28)
        form_layout.setSpacing(14)

        # Create 2-column grid
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        # Row 0: Name (full width)
        name_label = self.create_label("Mahsulot Nomi")
        self.name_input = self.create_input()
        if self.product:
            self.name_input.setText(self.product.name)
        grid.addWidget(name_label, 0, 0)
        grid.addWidget(self.name_input, 0, 1, 1, 3)

        # Row 1: Category (full width)
        category_label = self.create_label("Kategoriya")
        self.category_combo = self.create_combo()
        categories = CategoryService.get_all()
        self.category_combo.addItem("Kategoriyasiz", None)
        for cat in categories:
            self.category_combo.addItem(f"{cat.icon} {cat.name}", cat.id)
        if self.product and self.product.category_id:
            index = self.category_combo.findData(self.product.category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        grid.addWidget(category_label, 1, 0)
        grid.addWidget(self.category_combo, 1, 1, 1, 3)

        # Row 2: Selling Price | Cost Price
        selling_label = self.create_label("Sotuv Narxi")
        self.selling_price_input = self.create_money_input()
        if self.product:
            self.selling_price_input.setValue(self.product.selling_price)
        grid.addWidget(selling_label, 2, 0)
        grid.addWidget(self.selling_price_input, 2, 1)

        cost_label = self.create_label("Kelgan Narx")
        self.cost_price_input = self.create_money_input()
        if self.product:
            self.cost_price_input.setValue(self.product.cost_price)
        grid.addWidget(cost_label, 2, 2)
        grid.addWidget(self.cost_price_input, 2, 3)

        # Row 3: Quantity | Unit
        quantity_label = self.create_label("Ombor Soni")
        self.quantity_input = self.create_number_input()
        if self.product:
            self.quantity_input.setValue(self.product.quantity)
        grid.addWidget(quantity_label, 3, 0)
        grid.addWidget(self.quantity_input, 3, 1)

        unit_label = self.create_label("Birlik")
        self.unit_input = self.create_input()
        self.unit_input.setPlaceholderText("dona, kg, metr...")
        if self.product:
            self.unit_input.setText(self.product.unit)
        else:
            self.unit_input.setText("dona")
        grid.addWidget(unit_label, 3, 2)
        grid.addWidget(self.unit_input, 3, 3)
        form_layout.addLayout(grid)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 20, 0, 0)

        button_layout.addStretch()

        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.setFixedHeight(42)
        cancel_btn.setMinimumWidth(140)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e3a4f;
                color: #cbd5e1;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 500;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #2a4a61;
            }
            QPushButton:pressed {
                background-color: #152836;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("✓ Saqlash")
        save_btn.setFixedHeight(42)
        save_btn.setMinimumWidth(140)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)

        form_layout.addLayout(button_layout)

        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)

        self.setLayout(main_layout)

        # Set focus to first input
        self.name_input.setFocus()
        self.name_input.selectAll()

    def create_label(self, text):
        """Create styled label"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                color: #cbd5e1;
                font-size: 12px;
                font-weight: 500;
                padding: 0;
                margin: 0;
            }
        """)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        return label

    def create_input(self):
        """Create styled input"""
        input_field = QLineEdit()
        input_field.setFixedHeight(42)
        input_field.setStyleSheet("""
            QLineEdit {
                background-color: #f8fafc;
                color: #0f172a;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 0 14px;
                font-size: 13px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: 2px solid #4ca5b8;
                background-color: white;
            }
            QLineEdit:hover {
                background-color: white;
            }
        """)
        return input_field

    def create_combo(self):
        """Create styled combo box"""
        combo = QComboBox()
        combo.setFixedHeight(42)
        combo.setStyleSheet("""
            QComboBox {
                background-color: #f8fafc;
                color: #0f172a;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 0 14px;
                font-size: 13px;
                font-weight: 500;
            }
            QComboBox:focus {
                border: 2px solid #4ca5b8;
                background-color: white;
            }
            QComboBox:hover {
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                selection-background-color: #38bdf8;
                selection-color: #ffffff;
                padding: 4px;
            }
        """)
        return combo

    def create_money_input(self):
        """Create styled money input"""
        spin = QDoubleSpinBox()
        spin.setFixedHeight(42)
        spin.setMaximum(999999999)
        spin.setDecimals(0)
        spin.setGroupSeparatorShown(True)
        spin.setSuffix(" so'm")
        spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #f8fafc;
                color: #0f172a;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 0 14px;
                font-size: 13px;
                font-weight: 500;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #4ca5b8;
                background-color: white;
            }
            QDoubleSpinBox:hover {
                background-color: white;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 0px;
                border: none;
            }
        """)
        return spin

    def create_number_input(self):
        """Create styled number input"""
        spin = QDoubleSpinBox()
        spin.setFixedHeight(42)
        spin.setMaximum(999999999)
        spin.setDecimals(2)
        spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #f8fafc;
                color: #0f172a;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 0 14px;
                font-size: 13px;
                font-weight: 500;
            }
            QDoubleSpinBox:focus {
                border: 2px solid #4ca5b8;
                background-color: white;
            }
            QDoubleSpinBox:hover {
                background-color: white;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 0px;
                border: none;
            }
        """)
        return spin
