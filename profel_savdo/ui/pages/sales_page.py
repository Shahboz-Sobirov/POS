# -*- coding: utf-8 -*-
"""
Sales Page (F1) - SOTUV
Default page on app open
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QComboBox, QDoubleSpinBox,
                               QGroupBox, QDialog, QFormLayout,
                               QButtonGroup, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence, QFont
from services.product_service import ProductService
from services.category_service import CategoryService
from services.customer_service import CustomerService
from services.sale_service import SaleService
from ui.dialogs.quantity_edit_dialog import QuantityEditDialog
from utils.formatter import format_quantity
from utils.receipt_printer import ReceiptPrinter
from widgets.custom_alert import CustomAlert
from utils.error_logger import log_exception, get_user_friendly_message


class SalesPage(QWidget):
    def __init__(self, cashier_name="Admin"):
        super().__init__()
        self.cashier_name = cashier_name
        self.cart_items = []
        self.current_category_filter = None  # None = Barchasi
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        # COMPACT POS LAYOUT - Products-focused
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 4, 8, 8)  # Minimal top margin
        main_layout.setSpacing(4)  # Very tight spacing

        # ========================================
        # TOP SECTION: CART (LEFT) + PAYMENT (RIGHT) - 30% HEIGHT
        # ========================================
        top_section = QHBoxLayout()
        top_section.setSpacing(6)

        # LEFT: CART PANEL - VERY COMPACT
        cart_container = QVBoxLayout()
        cart_container.setSpacing(2)

        cart_label = QLabel("🛒 SAVAT")
        cart_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 700;
                color: #102331;
                padding: 0;
                margin: 2px 0;
            }
        """)
        cart_container.addWidget(cart_label)

        # Cart table - VERY COMPACT
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["MAHSULOT", "NARX", "MIQDOR", "JAMI"])

        # Column sizing
        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)

        self.cart_table.setColumnWidth(1, 90)
        self.cart_table.setColumnWidth(2, 80)
        self.cart_table.setColumnWidth(3, 100)

        header.setMinimumHeight(28)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setStretchLastSection(False)

        # Very compact styling
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setSelectionMode(QTableWidget.SingleSelection)
        self.cart_table.setShowGrid(True)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.verticalHeader().setDefaultSectionSize(32)  # Very compact rows
        self.cart_table.setMinimumHeight(260)  # Minimum height
        self.cart_table.setMaximumHeight(320)  # Maximum height
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable inline editing

        self.cart_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                gridline-color: #e2e8f0;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #38bdf8;
                color: white;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #e0f2fe;
            }
            QHeaderView::section {
                background-color: #102331;
                color: #f8fafc;
                padding: 6px 8px;
                border: none;
                font-weight: 700;
                font-size: 10px;
                text-transform: uppercase;
            }
            QHeaderView::section:first {
                border-top-left-radius: 6px;
                padding-left: 10px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 6px;
            }
        """)

        cart_container.addWidget(self.cart_table)

        # Cart buttons - VERY COMPACT
        cart_btn_layout = QHBoxLayout()
        cart_btn_layout.setSpacing(4)
        cart_btn_layout.setContentsMargins(0, 2, 0, 0)  # Minimal top margin

        remove_btn = QPushButton("🗑️ O'chirish")
        remove_btn.setObjectName("btnDanger")
        remove_btn.setMinimumHeight(28)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.clicked.connect(self.remove_from_cart)
        cart_btn_layout.addWidget(remove_btn)

        clear_btn = QPushButton("🧹 Tozalash")
        clear_btn.setObjectName("btnWarning")
        clear_btn.setMinimumHeight(28)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_cart)
        cart_btn_layout.addWidget(clear_btn)

        cart_container.addLayout(cart_btn_layout)

        top_section.addLayout(cart_container, 3)  # Cart takes 3 parts

        # RIGHT: PAYMENT PANEL - VERY COMPACT
        payment_container = QVBoxLayout()
        payment_container.setSpacing(4)

        payment_label = QLabel("💰 TO'LOV")
        payment_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 700;
                color: #102331;
                padding: 2px 0;
            }
        """)
        payment_container.addWidget(payment_label)

        # Customer - VERY COMPACT
        customer_layout = QVBoxLayout()
        customer_layout.setSpacing(2)

        customer_label = QLabel("Mijoz:")
        customer_label.setStyleSheet("font-size: 10px; font-weight: 600; color: #475569;")
        customer_layout.addWidget(customer_label)

        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumHeight(28)
        self.customer_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                padding: 3px 8px;
                font-size: 11px;
                font-weight: 600;
            }
            QComboBox:focus {
                border: 1px solid #38bdf8;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #0f172a;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                selection-background-color: #38bdf8;
                selection-color: white;
                font-size: 11px;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 8px;
                color: #0f172a;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e0f2fe;
            }
        """)
        customer_layout.addWidget(self.customer_combo)
        payment_container.addLayout(customer_layout)

        # Payment inputs - VERY COMPACT
        spinbox_style = """
            QDoubleSpinBox {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                padding: 3px 6px;
                font-size: 11px;
                font-weight: 600;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #38bdf8;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 0px;
            }
        """

        # Naqd
        naqd_layout = QVBoxLayout()
        naqd_layout.setSpacing(2)
        naqd_label = QLabel("💵 Naqd:")
        naqd_label.setStyleSheet("font-size: 10px; font-weight: 600; color: #475569;")
        naqd_layout.addWidget(naqd_label)
        self.naqd_input = QDoubleSpinBox()
        self.naqd_input.setMaximum(999999999)
        self.naqd_input.setMinimumHeight(28)
        self.naqd_input.setSuffix(" so'm")
        self.naqd_input.setStyleSheet(spinbox_style)
        self.naqd_input.valueChanged.connect(self.update_payment_status)
        naqd_layout.addWidget(self.naqd_input)
        payment_container.addLayout(naqd_layout)

        # Karta
        karta_layout = QVBoxLayout()
        karta_layout.setSpacing(2)
        karta_label = QLabel("💳 Karta:")
        karta_label.setStyleSheet("font-size: 10px; font-weight: 600; color: #475569;")
        karta_layout.addWidget(karta_label)
        self.karta_input = QDoubleSpinBox()
        self.karta_input.setMaximum(999999999)
        self.karta_input.setMinimumHeight(28)
        self.karta_input.setSuffix(" so'm")
        self.karta_input.setStyleSheet(spinbox_style)
        self.karta_input.valueChanged.connect(self.update_payment_status)
        karta_layout.addWidget(self.karta_input)
        payment_container.addLayout(karta_layout)

        # Click
        click_layout = QVBoxLayout()
        click_layout.setSpacing(2)
        click_label = QLabel("📱 Click:")
        click_label.setStyleSheet("font-size: 10px; font-weight: 600; color: #475569;")
        click_layout.addWidget(click_label)
        self.click_input = QDoubleSpinBox()
        self.click_input.setMaximum(999999999)
        self.click_input.setMinimumHeight(28)
        self.click_input.setSuffix(" so'm")
        self.click_input.setStyleSheet(spinbox_style)
        self.click_input.valueChanged.connect(self.update_payment_status)
        click_layout.addWidget(self.click_input)
        payment_container.addLayout(click_layout)

        # Qarz
        qarz_layout = QVBoxLayout()
        qarz_layout.setSpacing(2)
        qarz_label = QLabel("📋 Qarz:")
        qarz_label.setStyleSheet("font-size: 10px; font-weight: 600; color: #475569;")
        qarz_layout.addWidget(qarz_label)
        self.qarz_input = QDoubleSpinBox()
        self.qarz_input.setMaximum(999999999)
        self.qarz_input.setMinimumHeight(28)
        self.qarz_input.setSuffix(" so'm")
        self.qarz_input.setReadOnly(True)
        self.qarz_input.setStyleSheet(spinbox_style + """
            QDoubleSpinBox {
                background-color: #f1f5f9;
            }
        """)
        qarz_layout.addWidget(self.qarz_input)
        payment_container.addLayout(qarz_layout)

        # Total - COMPACT but visible
        self.total_label = QLabel("Jami: 0 so'm")
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #102331;
                background-color: #e0f2fe;
                border: 2px solid #38bdf8;
                border-radius: 6px;
                padding: 8px;
                margin: 4px 0;
            }
        """)
        payment_container.addWidget(self.total_label)

        # Payment status
        self.payment_status_label = QLabel()
        self.payment_status_label.setWordWrap(True)
        self.payment_status_label.setAlignment(Qt.AlignCenter)
        self.payment_status_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                font-weight: 600;
                padding: 2px;
            }
        """)
        payment_container.addWidget(self.payment_status_label)

        # Buttons - VERY COMPACT
        preview_btn = QPushButton("📄 Chek (F8)")
        preview_btn.setMinimumHeight(28)
        preview_btn.setCursor(Qt.PointingHandCursor)
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        preview_btn.clicked.connect(self.preview_invoice)
        payment_container.addWidget(preview_btn)

        complete_btn = QPushButton("✅ Yakunlash (F12)")
        complete_btn.setMinimumHeight(34)
        complete_btn.setCursor(Qt.PointingHandCursor)
        complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #16a34a;
            }
        """)
        complete_btn.clicked.connect(self.complete_sale)
        payment_container.addWidget(complete_btn)

        payment_container.addStretch()

        top_section.addLayout(payment_container, 2)  # Payment takes 2 parts

        main_layout.addLayout(top_section, 4)  # TOP AREA: stretch = 4

        # ========================================
        # BOTTOM SECTION: PRODUCTS - 70% HEIGHT (PRIMARY FOCUS)
        # ========================================
        products_label = QLabel("📦 MAHSULOTLAR")
        products_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-weight: 700;
                color: #102331;
                padding: 0;
                margin: 4px 0;
            }
        """)
        main_layout.addWidget(products_label)

        # Search - VERY COMPACT
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Qidirish... (Ctrl+F)")
        self.search_input.setMinimumHeight(30)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 0 10px;
                font-size: 12px;
                color: #0f172a;
            }
            QLineEdit:focus {
                border: 1px solid #38bdf8;
            }
        """)
        main_layout.addWidget(self.search_input)

        # Category tabs - COMPACT
        self.create_category_tabs(main_layout)

        # Products table - COMPACT
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["NOMI", "KATEGORIYA", "NARX", "OMBOR"])

        prod_header = self.products_table.horizontalHeader()
        prod_header.setSectionResizeMode(0, QHeaderView.Stretch)
        prod_header.setSectionResizeMode(1, QHeaderView.Fixed)
        prod_header.setSectionResizeMode(2, QHeaderView.Fixed)
        prod_header.setSectionResizeMode(3, QHeaderView.Fixed)

        self.products_table.setColumnWidth(1, 120)
        self.products_table.setColumnWidth(2, 100)
        self.products_table.setColumnWidth(3, 110)

        prod_header.setMinimumHeight(28)
        prod_header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.verticalHeader().setDefaultSectionSize(32)
        self.products_table.setMinimumHeight(260)  # Minimum height
        self.products_table.doubleClicked.connect(self.add_to_cart_from_table)

        self.products_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                gridline-color: #e2e8f0;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #38bdf8;
                color: white;
                font-weight: 600;
            }
            QTableWidget::item:hover {
                background-color: #e0f2fe;
            }
            QHeaderView::section {
                background-color: #102331;
                color: #f8fafc;
                padding: 6px 8px;
                border: none;
                font-weight: 700;
                font-size: 10px;
                text-transform: uppercase;
            }
            QHeaderView::section:first {
                border-top-left-radius: 6px;
                padding-left: 10px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 6px;
            }
        """)

        main_layout.addWidget(self.products_table, 5)  # BOTTOM AREA: stretch = 5

        # Add button - VERY COMPACT
        add_btn = QPushButton("➕ Savatga Qo'shish (Enter)")
        add_btn.setObjectName("btnSuccess")
        add_btn.setMinimumHeight(32)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: 600;
            }
        """)
        add_btn.clicked.connect(self.add_to_cart_from_table)
        main_layout.addWidget(add_btn)

        self.setLayout(main_layout)

        # Load data
        self.load_products()
        self.load_customers()

    def create_category_tabs(self, parent_layout):
        """Create category filter tabs - VERY COMPACT"""
        tabs_frame = QFrame()
        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(3)
        tabs_layout.setContentsMargins(0, 0, 0, 0)

        self.category_btn_group = QButtonGroup()

        # Very compact tab styling
        tab_style = """
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #e0f2fe;
                border-color: #38bdf8;
            }
            QPushButton:checked {
                background-color: #38bdf8;
                color: white;
                border-color: #38bdf8;
            }
        """

        # Barchasi
        all_btn = QPushButton("Barchasi")
        all_btn.setObjectName("categoryTab")
        all_btn.setCheckable(True)
        all_btn.setChecked(True)
        all_btn.setCursor(Qt.PointingHandCursor)
        all_btn.setMinimumHeight(32)
        all_btn.setStyleSheet(tab_style)
        all_btn.clicked.connect(lambda: self.filter_by_category(None))
        self.category_btn_group.addButton(all_btn)
        tabs_layout.addWidget(all_btn)

        # Load categories
        try:
            categories = CategoryService.get_all()
            for cat in categories:
                btn = QPushButton(f"{cat.icon} {cat.name}")
                btn.setObjectName("categoryTab")
                btn.setCheckable(True)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setMinimumHeight(32)
                btn.setStyleSheet(tab_style)
                btn.clicked.connect(lambda checked, c=cat.id: self.filter_by_category(c))
                self.category_btn_group.addButton(btn)
                tabs_layout.addWidget(btn)
        except Exception as e:
            print(f"Error loading categories: {e}")

        tabs_layout.addStretch()
        tabs_frame.setLayout(tabs_layout)
        parent_layout.addWidget(tabs_frame)

    def setup_shortcuts(self):
        """Setup shortcuts"""
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(
            lambda: self.search_input.setFocus()
        )
        QShortcut(QKeySequence("F8"), self).activated.connect(self.preview_invoice)
        QShortcut(QKeySequence("F9"), self).activated.connect(self.clear_cart)
        QShortcut(QKeySequence("F12"), self).activated.connect(self.complete_sale)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.remove_from_cart)
        QShortcut(QKeySequence("Ctrl+Delete"), self).activated.connect(self.clear_cart)
        QShortcut(QKeySequence("Return"), self).activated.connect(self.add_to_cart_from_table)
        QShortcut(QKeySequence("Enter"), self).activated.connect(self.add_to_cart_from_table)
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.edit_cart_quantity)
        QShortcut(QKeySequence("Ctrl+Enter"), self).activated.connect(self.edit_cart_quantity)

    def on_search_changed(self):
        """Search changed"""
        self.search_timer.stop()
        self.search_timer.start(300)

    def perform_search(self):
        """Perform search"""
        self.load_products()

    def filter_by_category(self, category_id):
        """Filter by category"""
        self.current_category_filter = category_id
        self.load_products()

    def load_products(self):
        """Load products"""
        try:
            query = self.search_input.text().strip()

            if query:
                products = ProductService.search(query)
            else:
                products = ProductService.get_all()

            # Filter by category
            if self.current_category_filter is not None:
                products = [p for p in products if p.category_id == self.current_category_filter]

            self.populate_products_table(products)

        except Exception as e:
            log_exception(e, "load_products")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def populate_products_table(self, products):
        """Populate products table"""
        self.products_table.setRowCount(len(products))

        for row, product in enumerate(products):
            # Name - VERY COMPACT
            name_item = QTableWidgetItem(product.name)
            name_font = name_item.font()
            name_font.setPointSize(12)
            name_item.setFont(name_font)
            self.products_table.setItem(row, 0, name_item)

            # Category
            cat_name = product.category.name if product.category else "-"
            cat_item = QTableWidgetItem(cat_name)
            cat_font = cat_item.font()
            cat_font.setPointSize(11)
            cat_item.setFont(cat_font)
            self.products_table.setItem(row, 1, cat_item)

            # Price - VERY COMPACT
            price_item = QTableWidgetItem(f"{product.selling_price:,.0f}")
            price_font = price_item.font()
            price_font.setPointSize(12)
            price_font.setWeight(QFont.Weight.DemiBold)
            price_item.setFont(price_font)
            self.products_table.setItem(row, 2, price_item)

            # Stock - with proper formatting
            stock_text = format_quantity(product.quantity, product.unit)
            stock_item = QTableWidgetItem(stock_text)
            stock_font = stock_item.font()
            stock_font.setPointSize(11)
            stock_item.setFont(stock_font)
            if product.quantity <= 0:
                stock_item.setBackground(Qt.red)
                stock_item.setForeground(Qt.white)
            elif product.quantity <= 5:
                stock_item.setBackground(Qt.yellow)
            self.products_table.setItem(row, 3, stock_item)

    def load_customers(self):
        """Load customers"""
        try:
            customers = CustomerService.get_all()
            self.customer_combo.clear()
            self.customer_combo.addItem("Mijoz tanlanmagan", None)
            for customer in customers:
                self.customer_combo.addItem(customer.full_name, customer.id)
        except Exception as e:
            print(f"Error loading customers: {e}")

    def add_to_cart_from_table(self):
        """Add selected product to cart"""
        selected = self.products_table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Mahsulot tanlanmagan!")
            return

        row = selected[0].row()
        query = self.search_input.text().strip()

        if query:
            products = ProductService.search(query)
        else:
            products = ProductService.get_all()

        if self.current_category_filter is not None:
            products = [p for p in products if p.category_id == self.current_category_filter]

        if row >= len(products):
            return

        product = products[row]

        if product.quantity <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Bu mahsulot omborda yo'q!")
            return

        # Show quantity dialog
        dialog = QuantityDialog(self, product)
        if dialog.exec() == QDialog.Accepted:
            quantity = dialog.quantity_input.value()
            price = dialog.price_input.value()

            if quantity > product.quantity:
                CustomAlert.show_warning(self, "Ogohlantirish", "Omborda yetarli mahsulot yo'q!")
                return

            # Check if already in cart
            for item in self.cart_items:
                if item['product'].id == product.id:
                    item['quantity'] += quantity
                    self.update_cart_table()
                    return

            # Add new item
            self.cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price
            })
            self.update_cart_table()

    def update_cart_table(self):
        """Update cart table"""
        self.cart_table.setRowCount(len(self.cart_items))

        total = 0
        for row, item in enumerate(self.cart_items):
            product = item['product']
            quantity = item['quantity']
            price = item['price']
            subtotal = quantity * price

            # Product name (left aligned) - COMPACT
            name_item = QTableWidgetItem(product.name)
            name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            name_font = name_item.font()
            name_font.setPointSize(13)
            name_font.setWeight(QFont.Weight.DemiBold)
            name_item.setFont(name_font)
            self.cart_table.setItem(row, 0, name_item)

            # Price (right aligned) - COMPACT
            price_item = QTableWidgetItem(f"{price:,.0f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            price_font = price_item.font()
            price_font.setPointSize(13)
            price_item.setFont(price_font)
            self.cart_table.setItem(row, 1, price_item)

            # Quantity (center aligned) - COMPACT with proper formatting
            qty_text = format_quantity(quantity, product.unit)
            qty_item = QTableWidgetItem(qty_text)
            qty_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            qty_font = qty_item.font()
            qty_font.setPointSize(13)
            qty_item.setFont(qty_font)
            self.cart_table.setItem(row, 2, qty_item)

            # Subtotal (right aligned) - COMPACT, BOLD
            subtotal_item = QTableWidgetItem(f"{subtotal:,.0f}")
            subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            subtotal_font = subtotal_item.font()
            subtotal_font.setPointSize(14)
            subtotal_font.setWeight(QFont.Weight.Bold)
            subtotal_item.setFont(subtotal_font)
            self.cart_table.setItem(row, 3, subtotal_item)

            total += subtotal

        self.total_label.setText(f"Jami: {total:,.0f} so'm")
        self.update_payment_status()

    def update_payment_status(self):
        """Update payment status"""
        total = sum(item['quantity'] * item['price'] for item in self.cart_items)

        naqd = self.naqd_input.value()
        karta = self.karta_input.value()
        click = self.click_input.value()

        paid = naqd + karta + click
        remaining = total - paid

        # Auto-calculate debt
        if remaining > 0:
            self.qarz_input.setValue(remaining)
        else:
            self.qarz_input.setValue(0)

        # Validation
        if paid > total:
            self.payment_status_label.setText("⚠️ To'lov summadan ortiq!")
            self.payment_status_label.setStyleSheet("color: red; font-weight: 600;")
        elif remaining == 0:
            self.payment_status_label.setText("✅ To'liq to'landi")
            self.payment_status_label.setStyleSheet("color: green; font-weight: 600;")
        else:
            self.payment_status_label.setText(f"Qoldi: {remaining:,.0f} so'm")
            self.payment_status_label.setStyleSheet("color: #3498db; font-weight: 600;")

    def remove_from_cart(self):
        """Remove from cart"""
        selected = self.cart_table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Mahsulot tanlanmagan!")
            return

        row = selected[0].row()
        if 0 <= row < len(self.cart_items):
            self.cart_items.pop(row)
            self.update_cart_table()

    def clear_cart(self):
        """Clear cart (F9)"""
        if self.cart_items:
            if CustomAlert.show_confirm(
                self, "Tasdiqlash",
                "Savatni tozalashni xohlaysizmi?"
            ):
                self.cart_items.clear()
                self.update_cart_table()
                self.naqd_input.setValue(0)
                self.karta_input.setValue(0)
                self.click_input.setValue(0)
                self.qarz_input.setValue(0)

    def edit_cart_quantity(self):
        """Edit cart quantity (Ctrl+Enter)"""
    def edit_cart_quantity(self):
        """Edit quantity in cart"""
        selected = self.cart_table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Mahsulot tanlanmagan!")
            return

        row = selected[0].row()
        if 0 <= row < len(self.cart_items):
            item = self.cart_items[row]
            product = item['product']
            current_qty = item['quantity']

            # Open quantity edit dialog
            dialog = QuantityEditDialog(self, product.name, current_qty, product.unit)
            if dialog.exec() == QDialog.Accepted:
                new_qty = dialog.get_quantity()
                if new_qty > 0:
                    item['quantity'] = new_qty
                    self.update_cart_table()
                else:
                    CustomAlert.show_warning(self, "Ogohlantirish", "Miqdor 0 dan katta bo'lishi kerak!")

    def preview_invoice(self):
        """Preview invoice (F8) - NO database save"""
        if not self.cart_items:
            CustomAlert.show_warning(self, "Ogohlantirish", "Savat bo'sh!")
            return

        payment_breakdown = self.build_payment_breakdown()
        customer_name = self.get_current_customer_name()
        success, message = ReceiptPrinter.preview_receipt(
            parent=self,
            cart_items=self.cart_items,
            payment_breakdown=payment_breakdown,
            cashier_name=self.cashier_name,
            customer_name=customer_name
        )
        if not success:
            CustomAlert.show_error(self, "Xato", message)

    def check_printer_available(self):
        """Check if printer is available"""
        return ReceiptPrinter.is_printer_available()

    def get_current_customer_name(self):
        """Get selected customer display name"""
        customer_name = self.customer_combo.currentText().strip()
        if not customer_name or customer_name == "Mijoz tanlanmagan":
            return None
        return customer_name

    def build_payment_breakdown(self):
        """Build payment breakdown from current UI values"""
        payment_breakdown = {}
        if self.naqd_input.value() > 0:
            payment_breakdown['naqd'] = self.naqd_input.value()
        if self.karta_input.value() > 0:
            payment_breakdown['karta'] = self.karta_input.value()
        if self.click_input.value() > 0:
            payment_breakdown['click'] = self.click_input.value()
        if self.qarz_input.value() > 0:
            payment_breakdown['qarz'] = self.qarz_input.value()
        return payment_breakdown

    def complete_sale(self):
        """Complete sale (F12) - REAL sale"""
        if not self.cart_items:
            CustomAlert.show_warning(self, "Ogohlantirish", "Savat bo'sh!")
            return

        customer_id = self.customer_combo.currentData()
        total_amount = sum(item['quantity'] * item['price'] for item in self.cart_items)

        naqd = self.naqd_input.value()
        karta = self.karta_input.value()
        click = self.click_input.value()
        qarz = self.qarz_input.value()

        total_paid = naqd + karta + click
        total_with_debt = total_paid + qarz

        # Validation
        # Check if any payment entered
        if total_with_debt <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "To'lov summasi kiritilmagan!")
            return

        # Check if payment is less than total
        if total_with_debt < total_amount:
            CustomAlert.show_warning(self, "Ogohlantirish", "To'lov jami summadan kam!")
            return

        # Check if payment is more than total
        if total_with_debt > total_amount:
            CustomAlert.show_warning(self, "Ogohlantirish", "To'lov summadan ortiq!")
            return

        # Check if debt requires customer
        if qarz > 0 and not customer_id:
            CustomAlert.show_warning(self, "Ogohlantirish", "Qarz uchun mijoz tanlanmagan!")
            return

        try:
            # Prepare items
            items = []
            for item in self.cart_items:
                items.append({
                    'product_id': item['product'].id,
                    'quantity': item['quantity'],
                    'price': item['price']
                })

            # Payment breakdown
            payment_breakdown = self.build_payment_breakdown()
            customer_name = self.get_current_customer_name()

            # Determine payment type
            if len(payment_breakdown) > 1:
                payment_type = "Mixed"
            elif naqd > 0:
                payment_type = "Naqd"
            elif karta > 0:
                payment_type = "Karta"
            elif click > 0:
                payment_type = "Click"
            else:
                payment_type = "Qarz"

            # Create sale
            sale = SaleService.create_sale(
                customer_id=customer_id,
                payment_type=payment_type,
                items=items,
                payment_breakdown=payment_breakdown,
                cashier=self.cashier_name
            )

            # Print receipt if printer is available
            if ReceiptPrinter.is_printer_available():
                success, message = ReceiptPrinter.print_receipt(
                    sale=sale,
                    cart_items=self.cart_items,
                    payment_breakdown=payment_breakdown,
                    cashier_name=self.cashier_name,
                    customer_name=customer_name
                )
                if not success:
                    CustomAlert.show_warning(
                        self,
                        "Ogohlantirish",
                        f"Savdo saqlandi, lekin chek chop etilmadi.\n\n{message}"
                    )
                else:
                    CustomAlert.show_success(
                        self,
                        "Muvaffaqiyat",
                        f"Savdo yakunlandi!\n\nChek #{sale.id}\nJami: {total_amount:,.0f} so'm\n\nChek printerga yuborildi."
                    )
            else:
                CustomAlert.show_success(
                    self,
                    "Muvaffaqiyat",
                    f"Savdo yakunlandi!\n\nChek #{sale.id}\nJami: {total_amount:,.0f} so'm\n\nPrinter topilmadi."
                )

            # Clear
            self.cart_items.clear()
            self.update_cart_table()
            self.naqd_input.setValue(0)
            self.karta_input.setValue(0)
            self.click_input.setValue(0)
            self.qarz_input.setValue(0)
            self.load_products()
            self.load_customers()

        except Exception as e:
            log_exception(e, "complete_sale")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def refresh(self):
        """Refresh page"""
        self.load_products()
        self.load_customers()


class QuantityDialog(QDialog):
    """Quantity input dialog"""
    def __init__(self, parent, product):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Miqdor")
        self.setModal(True)
        self.setup_ui()
        self.setup_shortcuts()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.reject)

    def setup_ui(self):
        layout = QFormLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Product name
        name_label = QLabel(self.product.name)
        name_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addRow("Mahsulot:", name_label)

        # Quantity
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setMaximum(self.product.quantity)
        self.quantity_input.setValue(1)
        self.quantity_input.setMinimumHeight(40)

        if self.product.unit.lower() in ['dona', 'ta', 'don']:
            self.quantity_input.setDecimals(0)
        else:
            self.quantity_input.setDecimals(2)

        self.quantity_input.setSuffix(f" {self.product.unit}")
        self.quantity_input.installEventFilter(self)
        layout.addRow("Miqdor:", self.quantity_input)

        # Price
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999999)
        self.price_input.setValue(self.product.selling_price)
        self.price_input.setMinimumHeight(40)
        self.price_input.setSuffix(" so'm")
        self.price_input.installEventFilter(self)
        layout.addRow("Narx:", self.price_input)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.setMinimumHeight(44)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        add_btn = QPushButton("Qo'shish")
        add_btn.setObjectName("btnSuccess")
        add_btn.setMinimumHeight(44)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.accept)
        btn_layout.addWidget(add_btn)

        layout.addRow("", btn_layout)

        self.setLayout(layout)
        self.setFixedSize(400, 280)

        # Set focus and select all
        self.quantity_input.setFocus()
        self.quantity_input.selectAll()

    def eventFilter(self, obj, event):
        """Handle focus events for auto-select and Enter key navigation"""
        from PySide6.QtCore import QEvent

        # Auto-select all text when focused
        if event.type() == QEvent.FocusIn:
            if isinstance(obj, QDoubleSpinBox):
                obj.selectAll()

        # Handle Enter key for navigation
        if event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                if obj == self.quantity_input:
                    self.price_input.setFocus()
                    return True
                elif obj == self.price_input:
                    self.accept()
                    return True

        return super().eventFilter(obj, event)
