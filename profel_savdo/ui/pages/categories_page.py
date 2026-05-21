# -*- coding: utf-8 -*-
"""
Categories Page (F6)
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog, QFormLayout, QLineEdit,
                               QColorDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from services.category_service import CategoryService
from widgets.custom_alert import CustomAlert
from utils.error_logger import log_exception, get_user_friendly_message


class CategoriesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.current_categories = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Title
        title = QLabel("Kategoriyalar")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        add_btn = QPushButton("➕ Yangi Kategoriya")
        add_btn.setObjectName("btnSuccess")
        add_btn.setMinimumHeight(44)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_category)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton("✏️ Tahrirlash")
        edit_btn.setMinimumHeight(44)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self.edit_category)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ O'chirish")
        delete_btn.setObjectName("btnDanger")
        delete_btn.setMinimumHeight(44)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self.delete_category)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Nomi", "Rang", "Icon"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_categories()

    def load_categories(self):
        """Load categories"""
        try:
            categories = CategoryService.get_all()
            self.current_categories = list(categories)
            self.table.setRowCount(len(categories))

            for row, cat in enumerate(categories):
                self.table.setItem(row, 0, QTableWidgetItem(cat.name))
                self.table.setItem(row, 1, QTableWidgetItem(cat.color or "#3498db"))
                self.table.setItem(row, 2, QTableWidgetItem(cat.icon or "📦"))

        except Exception as e:
            log_exception(e, "load_categories")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def add_category(self):
        """Add category"""
        dialog = CategoryDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                CategoryService.create(
                    name=dialog.name_input.text(),
                    color=dialog.color_value,
                    icon=dialog.icon_input.text()
                )
                self.load_categories()
                CustomAlert.show_success(self, "Muvaffaqiyat", "Kategoriya qo'shildi!")
            except Exception as e:
                log_exception(e, "add_category")
                message = str(e) if isinstance(e, ValueError) else get_user_friendly_message(e)
                CustomAlert.show_error(self, "Xato", message)

    def edit_category(self):
        """Edit category"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Kategoriya tanlanmagan!")
            return

        row = selected[0].row()
        if row >= len(self.current_categories):
            CustomAlert.show_warning(self, "Ogohlantirish", "Tanlangan kategoriya topilmadi!")
            return
        category = self.current_categories[row]

        dialog = CategoryDialog(self, category)
        if dialog.exec() == QDialog.Accepted:
            try:
                CategoryService.update(
                    category.id,
                    name=dialog.name_input.text(),
                    color=dialog.color_value,
                    icon=dialog.icon_input.text()
                )
                self.load_categories()
                CustomAlert.show_success(self, "Muvaffaqiyat", "Kategoriya tahrirlandi!")
            except Exception as e:
                log_exception(e, "edit_category")
                message = str(e) if isinstance(e, ValueError) else get_user_friendly_message(e)
                CustomAlert.show_error(self, "Xato", message)

    def delete_category(self):
        """Delete category"""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            CustomAlert.show_warning(self, "Ogohlantirish", "Kategoriya tanlanmagan!")
            return

        if CustomAlert.show_confirm(self, "Tasdiqlash", "Kategoriyani o'chirishni xohlaysizmi?"):
            row = selected[0].row()
            if row >= len(self.current_categories):
                CustomAlert.show_warning(self, "Ogohlantirish", "Tanlangan kategoriya topilmadi!")
                return
            category = self.current_categories[row]

            try:
                CategoryService.delete(category.id)
                self.load_categories()
                CustomAlert.show_success(self, "Muvaffaqiyat", "Kategoriya o'chirildi!")
            except Exception as e:
                log_exception(e, "delete_category")
                message = str(e) if isinstance(e, ValueError) else get_user_friendly_message(e)
                CustomAlert.show_error(self, "Xato", message)

    def refresh(self):
        """Refresh page"""
        self.load_categories()


class CategoryDialog(QDialog):
    """Category CRUD dialog"""
    def __init__(self, parent, category=None):
        super().__init__(parent)
        self.category = category
        self.color_value = category.color if category else "#3498db"
        self.setWindowTitle("Kategoriya" if not category else "Kategoriyani Tahrirlash")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Name
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(40)
        if self.category:
            self.name_input.setText(self.category.name)
        layout.addRow("Nomi:", self.name_input)

        # Color
        color_layout = QHBoxLayout()
        self.color_btn = QPushButton("Rang Tanlash")
        self.color_btn.setMinimumHeight(40)
        self.color_btn.setCursor(Qt.PointingHandCursor)
        self.color_btn.clicked.connect(self.choose_color)
        self.color_btn.setStyleSheet(f"background-color: {self.color_value};")
        color_layout.addWidget(self.color_btn)
        layout.addRow("Rang:", color_layout)

        # Icon
        self.icon_input = QLineEdit()
        self.icon_input.setMinimumHeight(40)
        self.icon_input.setPlaceholderText("📦")
        if self.category:
            self.icon_input.setText(self.category.icon or "📦")
        layout.addRow("Icon:", self.icon_input)

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
        self.setFixedSize(400, 300)

    def choose_color(self):
        """Choose color"""
        color = QColorDialog.getColor(QColor(self.color_value), self)
        if color.isValid():
            self.color_value = color.name()
            self.color_btn.setStyleSheet(f"background-color: {self.color_value};")
