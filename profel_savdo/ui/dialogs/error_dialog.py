# -*- coding: utf-8 -*-
"""
Professional Error Dialog
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTextEdit, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import traceback


class ErrorDialog(QDialog):
    """Modern professional error dialog with expandable technical details"""

    def __init__(self, parent, title, message, technical_details=None):
        super().__init__(parent)
        self.setWindowTitle("Xato")
        self.setModal(True)
        self.setFixedWidth(600)
        self.technical_details = technical_details
        self.details_visible = False
        self.setup_ui(title, message)

    def setup_ui(self, title, message):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QLabel(f"⚠️ {title}")
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

        # Content container
        content_container = QWidget()
        content_container.setStyleSheet("""
            QWidget {
                background-color: #13293a;
            }
        """)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(28, 28, 28, 28)
        content_layout.setSpacing(20)

        # User-friendly message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: #f8fafc;
                font-size: 14px;
                line-height: 1.6;
                padding: 0;
            }
        """)
        content_layout.addWidget(message_label)

        # Technical details section (collapsible)
        if self.technical_details:
            # Toggle button
            self.details_btn = QPushButton("📋 Texnik tafsilotlarni ko'rsatish")
            self.details_btn.setFixedHeight(36)
            self.details_btn.setCursor(Qt.PointingHandCursor)
            self.details_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e3a4f;
                    color: #cbd5e1;
                    border: none;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 500;
                    padding: 0 16px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2a4a61;
                }
            """)
            self.details_btn.clicked.connect(self.toggle_details)
            content_layout.addWidget(self.details_btn)

            # Technical details text area (hidden by default)
            self.details_text = QTextEdit()
            self.details_text.setReadOnly(True)
            self.details_text.setPlainText(self.technical_details)
            self.details_text.setFixedHeight(200)
            self.details_text.setVisible(False)

            # Monospace font for technical details
            mono_font = QFont("Consolas", 9)
            if not mono_font.exactMatch():
                mono_font = QFont("Courier New", 9)
            self.details_text.setFont(mono_font)

            self.details_text.setStyleSheet("""
                QTextEdit {
                    background-color: #0f1419;
                    color: #e8e8e8;
                    border: 1px solid #2a4a61;
                    border-radius: 8px;
                    padding: 12px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 9pt;
                }
            """)
            content_layout.addWidget(self.details_text)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.addStretch()

        close_btn = QPushButton("Yopish")
        close_btn.setFixedHeight(42)
        close_btn.setMinimumWidth(140)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 24px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        content_layout.addLayout(button_layout)

        content_container.setLayout(content_layout)
        main_layout.addWidget(content_container)

        self.setLayout(main_layout)

    def toggle_details(self):
        """Toggle technical details visibility"""
        self.details_visible = not self.details_visible
        self.details_text.setVisible(self.details_visible)

        if self.details_visible:
            self.details_btn.setText("📋 Texnik tafsilotlarni yashirish")
            self.setFixedHeight(self.sizeHint().height() + 200)
        else:
            self.details_btn.setText("📋 Texnik tafsilotlarni ko'rsatish")
            self.setFixedHeight(self.sizeHint().height())


def show_error(parent, title, message, exception=None):
    """
    Show professional error dialog

    Args:
        parent: Parent widget
        title: Error title (Uzbek)
        message: User-friendly message (Uzbek)
        exception: Optional exception object for technical details
    """
    technical_details = None
    if exception:
        technical_details = "".join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))

    dialog = ErrorDialog(parent, title, message, technical_details)
    dialog.exec()
