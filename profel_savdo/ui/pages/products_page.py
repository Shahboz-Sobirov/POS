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

        # ── Sarlavha ─────────────────────────────────────────────────────
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

        # ── Nomi ─────────────────────────────────────────────────────────
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(38)
        self.name_input.setPlaceholderText("Oyna nomi (masalan: 10 мм ок)")
        if self.product:
            self.name_input.setText(self.product.name)
        form.addRow("Oyna nomi:", self.name_input)

        # ── Kategoriya ────────────────────────────────────────────────────
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

        # ── Narxlar ───────────────────────────────────────────────────────
        self.selling_price_input = self.create_money_input()
        selling_price = (
            self.product.narx_per_kvm if self.product and self.product.narx_per_kvm is not None
            else (self.product.selling_price if self.product else 0)
        )
        self.selling_price_input.setValue(float(selling_price or 0))
        form.addRow("Sotuv narxi / KVM:", self.selling_price_input)

        self.cost_price_input = self.create_money_input()
        self.cost_price_input.setValue(float(self.product.cost_price) if self.product else 0)
        form.addRow("Kelgan narx / KVM:", self.cost_price_input)

        # ── O'lchamlar: Eni, Bo'yi (cm), Dona ────────────────────────────
        # Har ikki tur (glass va remnant) uchun ham
        self.eni_input = self._make_cm_spin()
        self.boyi_input = self._make_cm_spin()
        self.dona_input = self._make_dona_spin()

        # Mavjud qiymatlarni yuklash
        if self.product:
            existing_eni = self.product.eni if self.product.eni is not None else self.product.width
            existing_boyi = self.product.boyi if self.product.boyi is not None else self.product.height
            if existing_eni:
                self.eni_input.setValue(float(existing_eni) * 100)   # metr → cm
            if existing_boyi:
                self.boyi_input.setValue(float(existing_boyi) * 100)  # metr → cm
            # Dona: kvm / (eni*boyi) dan hisoblash
            if existing_eni and existing_boyi:
                one_kvm = float(existing_eni) * float(existing_boyi)
                qty = float(self.product.quantity or 0)
                if one_kvm > 0:
                    dona = round(qty / one_kvm)
                    self.dona_input.setValue(max(dona, 1))
                else:
                    self.dona_input.setValue(1)
            else:
                self.dona_input.setValue(1)

        self.eni_input.valueChanged.connect(self._update_kvm)
        self.boyi_input.valueChanged.connect(self._update_kvm)
        self.dona_input.valueChanged.connect(self._update_kvm)

        form.addRow("Eni (cm):", self.eni_input)
        form.addRow("Bo'yi (cm):", self.boyi_input)
        form.addRow("Dona (soni):", self.dona_input)

        # ── KVM — avtomatik hisoblangan ───────────────────────────────────
        self.kvm_label = QLabel("0.0000 kvm")
        self.kvm_label.setMinimumHeight(38)
        self.kvm_label.setStyleSheet(
            "background-color: #e0f2fe; border: 1px solid #38bdf8; "
            "border-radius: 6px; padding: 6px 12px; "
            "font-size: 14px; font-weight: 700; color: #0369a1;"
        )
        form.addRow("KVM (avtomatik):", self.kvm_label)

        # Ombor qo'lda kiritish (glass uchun ixtiyoriy, remnant uchun auto)
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setDecimals(4)
        self.quantity_input.setMaximum(999999999)
        self.quantity_input.setGroupSeparatorShown(True)
        self.quantity_input.setSuffix(" kvm")
        self.quantity_input.setMinimumHeight(38)
        self.quantity_input.setValue(float(self.product.quantity) if self.product else 0)

        if self.product_type == "remnant":
            # Qoldiq uchun ombor avtomatik = eni*boyi
            self.quantity_input.setReadOnly(True)
            self.quantity_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
            self.quantity_input.setStyleSheet(
                "QDoubleSpinBox { background-color: #f0f0f0; color: #64748b; }"
            )
            form.addRow("Ombor (auto):", self.quantity_input)
        else:
            # Asosiy oyna uchun ombor qo'lda kiritiladi (dona*kvm hisoblab beriladi)
            self.quantity_input.setToolTip("Eni, Bo'yi va Dona kiritilsa avtomatik hisoblanadi")
            form.addRow("Ombor (kvm):", self.quantity_input)

        # ── Eslatma ───────────────────────────────────────────────────────
        self.note_input = QTextEdit()
        self.note_input.setMaximumHeight(60)
        self.note_input.setPlaceholderText("Eslatma (ixtiyoriy)")
        if self.product and self.product.note:
            self.note_input.setPlainText(self.product.note)
        form.addRow("Eslatma:", self.note_input)

        body.addLayout(form)

        # ── Tugmalar ──────────────────────────────────────────────────────
        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        cancel_btn = QPushButton("Bekor qilish")
        cancel_btn.setMinimumHeight(38)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        save_btn = QPushButton("Saqlash")
        save_btn.setObjectName("btnSuccess")
        save_btn.setMinimumHeight(38)
        save_btn.clicked.connect(self.save)
        buttons.addWidget(save_btn)

        body.addLayout(buttons)
        root.addLayout(body)
        self.setLayout(root)
        self.setFixedSize(560, 580)

        # Boshlang'ich hisoblash
        self._update_kvm()

    # ── Spin box yaratish yordamchilari ───────────────────────────────────

    def _make_cm_spin(self):
        spin = QDoubleSpinBox()
        spin.setDecimals(1)
        spin.setMaximum(99999)
        spin.setMinimum(0)
        spin.setSingleStep(1)
        spin.setSuffix(" cm")
        spin.setMinimumHeight(38)
        return spin

    def _make_dona_spin(self):
        spin = QDoubleSpinBox()
        spin.setDecimals(0)
        spin.setMaximum(99999)
        spin.setMinimum(1)
        spin.setSingleStep(1)
        spin.setSuffix(" dona")
        spin.setMinimumHeight(38)
        spin.setValue(1)
        return spin

    # ── KVM avtomatik hisoblash ───────────────────────────────────────────

    def _update_kvm(self):
        """Eni × Bo'yi × Dona → KVM. Label va ombor maydonini yangilaydi."""
        eni_cm  = self.eni_input.value()
        boyi_cm = self.boyi_input.value()
        dona    = int(self.dona_input.value())

        if eni_cm > 0 and boyi_cm > 0:
            one_kvm = (eni_cm * boyi_cm) / 10000.0   # cm² → m²
            total_kvm = round(one_kvm * dona, 4)
        else:
            one_kvm   = 0.0
            total_kvm = 0.0

        # KVM label yangilash
        if eni_cm > 0 and boyi_cm > 0:
            self.kvm_label.setText(
                f"{total_kvm:.4f} kvm  "
                f"({eni_cm:.1f}cm × {boyi_cm:.1f}cm × {dona} dona)"
            )
        else:
            self.kvm_label.setText("0.0000 kvm  —  Eni va Bo'yi kiriting")

        # Ombor maydonini yangilash
        if self.product_type == "remnant":
            # Qoldiq uchun har doim avtomatik (1 dona)
            self.quantity_input.setValue(one_kvm)
        else:
            # Asosiy oyna uchun: agar eni/boyi kiritilgan bo'lsa avtohisob
            if eni_cm > 0 and boyi_cm > 0:
                self.quantity_input.setValue(total_kvm)

    # ──────────────────────────────────────────────────────────────────────

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
        if self.eni_input.value() <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Eni 0 dan katta bo'lishi kerak!")
            self.eni_input.setFocus()
            return
        if self.boyi_input.value() <= 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Bo'yi 0 dan katta bo'lishi kerak!")
            self.boyi_input.setFocus()
            return
        if self.quantity_input.value() < 0:
            CustomAlert.show_warning(self, "Ogohlantirish", "Ombor manfiy bo'lishi mumkin emas!")
            return
        self.accept()

    def get_data(self):
        eni_cm  = self.eni_input.value()
        boyi_cm = self.boyi_input.value()
        dona    = int(self.dona_input.value())

        # cm → metr
        eni_m  = eni_cm  / 100.0
        boyi_m = boyi_cm / 100.0

        one_kvm   = round(eni_m * boyi_m, 6)
        total_kvm = round(one_kvm * dona, 4)

        narx_per_kvm = self.selling_price_input.value()
        return {
            'name':         self.name_input.text().strip(),
            'category_id':  self.category_combo.currentData(),
            'selling_price': narx_per_kvm,
            'narx_per_kvm': narx_per_kvm,
            'cost_price':   self.cost_price_input.value(),
            'quantity':     self.quantity_input.value(),
            'unit':         'kvm',
            'barcode':      None,
            'product_type': self.product_type,
            'eni':          eni_m,
            'boyi':         boyi_m,
            'kvm':          total_kvm,
            'width':        eni_m,
            'height':       boyi_m,
            'area_sqm':     total_kvm,
            'note':         self.note_input.toPlainText().strip() or None,
        }
