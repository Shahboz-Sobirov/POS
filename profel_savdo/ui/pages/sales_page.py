# -*- coding: utf-8 -*-
"""
Sales Page (F1) - OYNA SOTUV
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QVBoxLayout,
    QWidget,
)

from services.category_service import CategoryService
from services.customer_service import CustomerService
from services.product_service import ProductService
from services.sale_service import SaleService
from utils.error_logger import get_user_friendly_message, log_exception
from utils.formatter import (
    format_meters,
    format_quantity_display,
    format_square_meters,
)
from ui.dialogs.glass_order_dialog import GlassOrderDialog
from utils.receipt_printer import ReceiptPrinter
from widgets.custom_alert import CustomAlert


class SalesPage(QWidget):
    def __init__(self, cashier_name="Admin"):
        super().__init__()
        self.cashier_name = cashier_name
        self.cart_items = []
        self.current_products = []
        self.current_category_filter = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(6)

        # ── Yuqori qism: Savat (chap) + To'lov (o'ng) ────────────────────
        top_section = QHBoxLayout()
        top_section.setSpacing(10)

        cart_panel = self.create_cart_panel()
        payment_panel = self.create_payment_panel()
        top_section.addLayout(cart_panel, 5)   # savat kengroq
        top_section.addLayout(payment_panel, 3) # to'lov torroq

        # stretch=2 — ekranning ~30% ni oladi (oldin 3/9 = 33%)
        main_layout.addLayout(top_section, 2)

        # ── Qidiruv ───────────────────────────────────────────────────────
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        products_title = QLabel("Sotiladigan Oynalar")
        products_title.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #102331;"
        )
        search_row.addWidget(products_title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Oyna nomi bo'yicha qidirish...")
        self.search_input.setMinimumHeight(30)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setStyleSheet("font-size: 12px; padding: 4px 8px;")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_row.addWidget(self.search_input, 1)

        main_layout.addLayout(search_row)

        self.create_category_tabs(main_layout)

        # ── Mahsulotlar jadvali ───────────────────────────────────────────
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(
            ["Oyna", "Kategoriya", "Narx/KVM", "Ombor", "Birlik", "Eslatma"]
        )
        products_header = self.products_table.horizontalHeader()
        products_header.setSectionResizeMode(0, QHeaderView.Stretch)
        products_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        products_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        products_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        products_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        products_header.setSectionResizeMode(5, QHeaderView.Stretch)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SingleSelection)
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.verticalHeader().setDefaultSectionSize(32)
        self.products_table.setWordWrap(False)
        self.products_table.setStyleSheet("font-size: 12px;")
        self.products_table.doubleClicked.connect(self.add_to_cart_from_table)
        # stretch=5 — ekranning ~62% ni oladi
        main_layout.addWidget(self.products_table, 5)

        add_btn = QPushButton("Savatga qo'shish")
        add_btn.setObjectName("btnSuccess")
        add_btn.setMinimumHeight(34)
        add_btn.setStyleSheet("font-size: 13px; font-weight: 600;")
        add_btn.clicked.connect(self.add_to_cart_from_table)
        main_layout.addWidget(add_btn)

        self.setLayout(main_layout)

        self.load_products()
        self.load_customers()

    def create_cart_panel(self):
        cart_container = QVBoxLayout()
        cart_container.setSpacing(4)
        cart_container.setContentsMargins(4, 4, 4, 4)

        cart_label = QLabel("Savat")
        cart_label.setStyleSheet(
            "font-size: 12px; font-weight: 700; color: #102331;"
        )
        cart_container.addWidget(cart_label)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels(
            ["Oyna", "Eni", "Bo'yi", "KVM", "Narx/KVM", "Jami"]
        )
        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setSelectionMode(QTableWidget.SingleSelection)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.verticalHeader().setDefaultSectionSize(28)
        self.cart_table.setWordWrap(False)
        self.cart_table.setStyleSheet("font-size: 11px;")
        self.cart_table.doubleClicked.connect(self.edit_cart_quantity)
        # setMaximumHeight — savat 5 qatordan oshmasin
        self.cart_table.setMaximumHeight(200)
        cart_container.addWidget(self.cart_table)

        cart_buttons = QHBoxLayout()
        cart_buttons.setSpacing(5)
        remove_btn = QPushButton("O'chirish")
        remove_btn.setObjectName("btnDanger")
        remove_btn.setMinimumHeight(26)
        remove_btn.setStyleSheet("font-size: 11px;")
        remove_btn.clicked.connect(self.remove_from_cart)
        cart_buttons.addWidget(remove_btn)

        edit_btn = QPushButton("O'zgartirish")
        edit_btn.setMinimumHeight(26)
        edit_btn.setStyleSheet("font-size: 11px;")
        edit_btn.clicked.connect(self.edit_cart_quantity)
        cart_buttons.addWidget(edit_btn)

        clear_btn = QPushButton("Tozalash")
        clear_btn.setObjectName("btnWarning")
        clear_btn.setMinimumHeight(26)
        clear_btn.setStyleSheet("font-size: 11px;")
        clear_btn.clicked.connect(self.clear_cart)
        cart_buttons.addWidget(clear_btn)

        cart_container.addLayout(cart_buttons)
        return cart_container

    def create_payment_panel(self):
        payment_container = QVBoxLayout()
        payment_container.setSpacing(4)
        payment_container.setContentsMargins(4, 4, 4, 4)

        payment_label = QLabel("To'lov")
        payment_label.setStyleSheet(
            "font-size: 12px; font-weight: 700; color: #102331;"
        )
        payment_container.addWidget(payment_label)

        # Mijoz
        customer_row = QHBoxLayout()
        customer_row.setSpacing(4)
        cust_lbl = QLabel("Mijoz:")
        cust_lbl.setStyleSheet("font-size: 11px; color: #475569;")
        cust_lbl.setFixedWidth(44)
        customer_row.addWidget(cust_lbl)
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumHeight(26)
        self.customer_combo.setStyleSheet("font-size: 11px;")
        customer_row.addWidget(self.customer_combo)
        payment_container.addLayout(customer_row)

        # To'lov inputlari — ixcham qatorlarda
        self.naqd_input  = self.create_money_input(self.update_payment_status)
        self.karta_input = self.create_money_input(self.update_payment_status)
        self.click_input = self.create_money_input(self.update_payment_status)
        self.qarz_input  = self.create_money_input(None, read_only=True)

        payment_container.addWidget(self.wrap_payment_input("Naqd",  self.naqd_input))
        payment_container.addWidget(self.wrap_payment_input("Karta", self.karta_input))
        payment_container.addWidget(self.wrap_payment_input("Click", self.click_input))
        payment_container.addWidget(self.wrap_payment_input("Qarz",  self.qarz_input))

        # Jami label
        self.total_label = QLabel("Jami: 0 so'm")
        self.total_label.setAlignment(Qt.AlignCenter)
        self.total_label.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #102331;"
            "background-color: #e0f2fe; border: 2px solid #38bdf8;"
            "border-radius: 6px; padding: 6px; margin-top: 2px;"
        )
        payment_container.addWidget(self.total_label)

        # Status
        self.payment_status_label = QLabel()
        self.payment_status_label.setWordWrap(True)
        self.payment_status_label.setAlignment(Qt.AlignCenter)
        self.payment_status_label.setStyleSheet("font-size: 11px;")
        payment_container.addWidget(self.payment_status_label)

        # Tugmalar
        preview_btn = QPushButton("Chek (F8)")
        preview_btn.setMinimumHeight(28)
        preview_btn.setStyleSheet("font-size: 11px;")
        preview_btn.clicked.connect(self.preview_invoice)
        payment_container.addWidget(preview_btn)

        complete_btn = QPushButton("Yakunlash (F12)")
        complete_btn.setObjectName("btnSuccess")
        complete_btn.setMinimumHeight(34)
        complete_btn.setStyleSheet("font-size: 13px; font-weight: 600;")
        complete_btn.clicked.connect(self.complete_sale)
        payment_container.addWidget(complete_btn)

        payment_container.addStretch()
        return payment_container

    def create_money_input(self, slot, read_only=False):
        input_widget = QDoubleSpinBox()
        input_widget.setMaximum(999999999)
        input_widget.setDecimals(0)
        input_widget.setGroupSeparatorShown(True)
        input_widget.setSuffix(" so'm")
        input_widget.setMinimumHeight(26)
        input_widget.setStyleSheet("font-size: 11px;")
        input_widget.setReadOnly(read_only)
        if slot:
            input_widget.valueChanged.connect(slot)
        return input_widget

    def wrap_payment_input(self, title, widget):
        wrapper = QGroupBox(title)
        wrapper.setStyleSheet(
            "QGroupBox { font-size: 10px; font-weight: 600; color: #475569;"
            "border: 1px solid #cbd5e1; border-radius: 4px;"
            "margin-top: 6px; padding-top: 2px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 6px; }"
        )
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 6, 5, 4)
        layout.setSpacing(0)
        layout.addWidget(widget)
        wrapper.setLayout(layout)
        return wrapper

    def create_category_tabs(self, parent_layout):
        tabs_frame = QFrame()
        tabs_layout = QHBoxLayout()
        tabs_layout.setSpacing(6)
        tabs_layout.setContentsMargins(0, 0, 0, 0)

        self.category_btn_group = QButtonGroup(self)
        self.category_btn_group.setExclusive(True)

        all_btn = QPushButton("Barchasi")
        all_btn.setCheckable(True)
        all_btn.setChecked(True)
        all_btn.clicked.connect(lambda: self.filter_by_category(None))
        tabs_layout.addWidget(all_btn)
        self.category_btn_group.addButton(all_btn)

        try:
            for category in CategoryService.get_all():
                btn = QPushButton(category.name)
                btn.setCheckable(True)
                btn.clicked.connect(
                    lambda checked=False, category_id=category.id: self.filter_by_category(category_id)
                )
                tabs_layout.addWidget(btn)
                self.category_btn_group.addButton(btn)
        except Exception as e:
            print(f"Error loading categories: {e}")

        tabs_layout.addStretch()
        tabs_frame.setLayout(tabs_layout)
        parent_layout.addWidget(tabs_frame)

    def setup_shortcuts(self):
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
        self.search_timer.stop()
        self.search_timer.start(300)

    def perform_search(self):
        self.load_products()

    def filter_by_category(self, category_id):
        self.current_category_filter = category_id
        self.load_products()

    def load_products(self):
        try:
            query = self.search_input.text().strip()
            products = ProductService.search(query) if query else ProductService.get_all()
            if self.current_category_filter is not None:
                products = [p for p in products if p.category_id == self.current_category_filter]
            products = [p for p in products if float(p.quantity or 0) > 0]
            self.current_products = products
            self.populate_products_table(products)
        except Exception as e:
            log_exception(e, "load_products")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def populate_products_table(self, products):
        self.products_table.setRowCount(len(products))

        for row, product in enumerate(products):
            name = product.name
            if product.is_remnant:
                name = f"{name} [Qoldiq]"

            self.products_table.setItem(row, 0, QTableWidgetItem(name))
            self.products_table.setItem(row, 1, QTableWidgetItem(product.category.name if product.category else "-"))
            price_value = product.narx_per_kvm if product.narx_per_kvm is not None else product.selling_price
            self.products_table.setItem(row, 2, QTableWidgetItem(f"{price_value:,.0f}"))
            qty = float(product.quantity or 0)
            stock_item = QTableWidgetItem(format_quantity_display(qty, product.unit or "kvm"))
            if qty <= 0:
                stock_item.setBackground(Qt.red)
                stock_item.setForeground(Qt.white)
            elif qty <= 1:
                stock_item.setBackground(Qt.yellow)
            self.products_table.setItem(row, 3, stock_item)
            self.products_table.setItem(row, 4, QTableWidgetItem((product.unit or "kvm").upper()))
            self.products_table.setItem(row, 5, QTableWidgetItem(product.note or "-"))

            for col in range(1, self.products_table.columnCount()):
                item = self.products_table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
        self.products_table.resizeRowsToContents()

    def load_customers(self):
        try:
            customers = CustomerService.get_all()
            self.customer_combo.clear()
            self.customer_combo.addItem("Mijoz tanlanmagan", None)
            for customer in customers:
                self.customer_combo.addItem(customer.full_name, customer.id)
        except Exception as e:
            print(f"Error loading customers: {e}")

    def add_to_cart_from_table(self):
        selected = self.products_table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Oyna tanlanmagan!")
            return

        row = selected[0].row()
        if row >= len(self.current_products):
            return

        product = self.current_products[row]
        if product.quantity <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Bu oyna omborda qolmagan!")
            return

        available_stock = self.get_available_stock(product)
        dialog = GlassOrderDialog(self, product, available_stock=available_stock)
        if dialog.exec() != QDialog.Accepted:
            return

        cart_item = dialog.get_cart_item()
        self.cart_items.append(cart_item)
        self.update_cart_table()

    def update_cart_table(self):
        self.cart_table.setRowCount(len(self.cart_items))

        total = 0
        for row, item in enumerate(self.cart_items):
            kvm = float(item['kvm'])
            subtotal = float(item.get('jami', kvm * item['narx_per_kvm']))

            name_item = QTableWidgetItem(item['product'].name)
            name_font = name_item.font()
            name_font.setPointSize(11)
            name_font.setWeight(QFont.Weight.DemiBold)
            name_item.setFont(name_font)
            self.cart_table.setItem(row, 0, name_item)

            self.cart_table.setItem(row, 1, QTableWidgetItem(format_meters(item['eni'])))
            self.cart_table.setItem(row, 2, QTableWidgetItem(format_meters(item['boyi'])))
            self.cart_table.setItem(row, 3, QTableWidgetItem(format_square_meters(kvm)))
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"{item['narx_per_kvm']:,.0f}"))
            self.cart_table.setItem(row, 5, QTableWidgetItem(f"{subtotal:,.0f}"))
            for col in range(self.cart_table.columnCount()):
                table_item = self.cart_table.item(row, col)
                if table_item:
                    table_item.setTextAlignment(Qt.AlignCenter)
            total += subtotal

        self.total_label.setText(f"Jami: {total:,.0f} so'm")
        self.cart_table.resizeRowsToContents()
        self.update_payment_status()

    def update_payment_status(self):
        total = self.calculate_cart_total()
        naqd = self.naqd_input.value()
        karta = self.karta_input.value()
        click = self.click_input.value()
        paid = naqd + karta + click
        remaining = total - paid

        self.qarz_input.setValue(remaining if remaining > 0 else 0)

        if paid > total:
            self.payment_status_label.setText("To'lov summadan ortiq!")
            self.payment_status_label.setStyleSheet("color: red; font-weight: 600;")
        elif total == 0:
            self.payment_status_label.setText("Savat bo'sh")
            self.payment_status_label.setStyleSheet("color: #64748b; font-weight: 600;")
        elif remaining == 0:
            self.payment_status_label.setText("To'liq to'landi")
            self.payment_status_label.setStyleSheet("color: green; font-weight: 600;")
        else:
            self.payment_status_label.setText(f"Qoldi: {remaining:,.0f} so'm")
            self.payment_status_label.setStyleSheet("color: #3498db; font-weight: 600;")

    def remove_from_cart(self):
        selected = self.cart_table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Savatdan o'chirish uchun qator tanlang!")
            return

        row = selected[0].row()
        if 0 <= row < len(self.cart_items):
            self.cart_items.pop(row)
            self.update_cart_table()

    def clear_cart(self):
        if not self.cart_items:
            return
        if not CustomAlert.show_confirm(self, "Tasdiqlash", "Savatni tozalashni xohlaysizmi?"):
            return

        self.cart_items.clear()
        self.update_cart_table()
        self.naqd_input.setValue(0)
        self.karta_input.setValue(0)
        self.click_input.setValue(0)
        self.qarz_input.setValue(0)

    def edit_cart_quantity(self):
        selected = self.cart_table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Savatdagi oyna tanlanmagan!")
            return

        row = selected[0].row()
        if not (0 <= row < len(self.cart_items)):
            return

        current_item = self.cart_items[row]
        available_stock = self.get_available_stock(current_item['product'], excluding_row=row)
        dialog = GlassOrderDialog(
            self,
            current_item['product'],
            current_item,
            available_stock=available_stock,
        )
        if dialog.exec() != QDialog.Accepted:
            return

        updated_item = dialog.get_cart_item()
        self.cart_items[row] = updated_item
        self.update_cart_table()

    def preview_invoice(self):
        """F8 — ro'yxat cheki, to'g'ridan-to'g'ri printerga yuboriladi."""
        if not self.cart_items:
            CustomAlert.show_warning(self, "Ogohlantirish", "Savat bo'sh!")
            return

        customer_name = self.get_current_customer_name()
        success, message = ReceiptPrinter.print_preview_receipt(
            cart_items=self.cart_items,
            cashier_name=self.cashier_name,
            customer_name=customer_name,
        )
        if not success:
            CustomAlert.show_error(self, "Printer Xatosi", message)
        else:
            CustomAlert.show_success(
                self,
                "Muvaffaqiyat",
                f"Ro'yxat cheki printerga yuborildi.\n\n"
                f"(Savdo hali yakunlanmagan — faqat ro'yxat)"
            )

    def check_printer_available(self):
        return ReceiptPrinter.is_printer_available()

    def get_current_customer_name(self):
        customer_name = self.customer_combo.currentText().strip()
        if not customer_name or customer_name == "Mijoz tanlanmagan":
            return None
        return customer_name

    def build_payment_breakdown(self):
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
        if not self.cart_items:
            CustomAlert.show_warning(self, "Ogohlantirish", "Savat bo'sh!")
            return

        customer_id = self.customer_combo.currentData()
        total_amount = self.calculate_cart_total()

        naqd = self.naqd_input.value()
        karta = self.karta_input.value()
        click = self.click_input.value()
        qarz = self.qarz_input.value()

        total_paid = naqd + karta + click
        total_with_debt = total_paid + qarz

        if total_with_debt <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "To'lov summasi kiritilmagan!")
            return

        if total_with_debt < total_amount:
            CustomAlert.show_warning(self, "Ogohlantirish", "To'lov jami summadan kam!")
            return

        if total_with_debt > total_amount:
            CustomAlert.show_warning(self, "Ogohlantirish", "To'lov summadan ortiq!")
            return

        if qarz > 0 and not customer_id:
            CustomAlert.show_warning(self, "Ogohlantirish", "Qarz uchun mijoz tanlanmagan!")
            return

        try:
            items = []
            for item in self.cart_items:
                items.append({
                    'product_id': item['product'].id,
                    'quantity': item['kvm'],
                    'eni': item['eni'],
                    'boyi': item['boyi'],
                    'kvm': item['kvm'],
                    'narx_per_kvm': item['narx_per_kvm'],
                    'width': item['width'],
                    'height': item['height'],
                    'area_sqm': item['area_sqm'],
                    'price': item['price'],
                })

            payment_breakdown = self.build_payment_breakdown()
            customer_name = self.get_current_customer_name()

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

            sale = SaleService.create_sale(
                customer_id=customer_id,
                payment_type=payment_type,
                items=items,
                payment_breakdown=payment_breakdown,
                cashier=self.cashier_name
            )

            # Chekni to'g'ridan-to'g'ri printerga yuborish
            success, print_msg = ReceiptPrinter.print_receipt(
                sale=sale,
                cart_items=self.cart_items,
                payment_breakdown=payment_breakdown,
                cashier_name=self.cashier_name,
                customer_name=customer_name,
            )

            if success:
                CustomAlert.show_success(
                    self,
                    "Muvaffaqiyat",
                    f"Savdo yakunlandi!\n\nChek #{sale.id}\n"
                    f"Jami: {total_amount:,.0f} so'm\n\n"
                    f"{print_msg}"
                )
            else:
                # Savdo saqlandi, lekin printer xatosi
                CustomAlert.show_warning(
                    self,
                    "Savdo Saqlandi",
                    f"Savdo muvaffaqiyatli saqlandi!\n\nChek #{sale.id}\n"
                    f"Jami: {total_amount:,.0f} so'm\n\n"
                    f"⚠ Chek chop etilmadi:\n{print_msg}"
                )

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
        self.load_products()
        self.load_customers()

    def calculate_cart_total(self):
        total = 0.0
        for item in self.cart_items:
            kvm = float(item.get('kvm') or 0)
            narx = float(item.get('narx_per_kvm') or 0)
            jami = float(item.get('jami') or (kvm * narx))
            total += jami
        return total

    def get_reserved_kvm(self, product_id, excluding_row=None):
        reserved = 0.0
        for row, item in enumerate(self.cart_items):
            if excluding_row is not None and row == excluding_row:
                continue
            if item['product'].id == product_id:
                reserved += float(item.get('kvm') or 0)
        return reserved

    def get_available_stock(self, product, excluding_row=None):
        reserved = self.get_reserved_kvm(product.id, excluding_row=excluding_row)
        return max(float(product.quantity or 0) - reserved, 0)
