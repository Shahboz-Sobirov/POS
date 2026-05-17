# -*- coding: utf-8 -*-
"""
Custom Alert Dialog - Modern Dark Theme
Professional POS style alerts
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont


class CustomAlert(QDialog):
    """Modern dark theme alert dialog"""

    # Alert types
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    CONFIRM = "confirm"

    def __init__(self, parent=None, alert_type=INFO, title="", message=""):
        super().__init__(parent)
        self.alert_type = alert_type
        self.result_value = False
        self.setup_ui(title, message)
        self.setup_animation()

    def setup_ui(self, title, message):
        """Setup UI"""
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(420)
        self.setMinimumHeight(160)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Container with dark background
        container = QVBoxLayout()
        container.setContentsMargins(24, 24, 24, 24)
        container.setSpacing(16)

        # Icon + Title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Icon
        icon_label = QLabel(self.get_icon())
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                color: {self.get_icon_color()};
            }}
        """)
        header_layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: 700;
            }
        """)
        header_layout.addWidget(title_label, 1)

        container.addLayout(header_layout)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                color: #E2E8F0;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        container.addWidget(message_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()

        if self.alert_type == self.CONFIRM:
            # Cancel button
            cancel_btn = QPushButton("Bekor qilish")
            cancel_btn.setMinimumHeight(38)
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #475569;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0 20px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #64748b;
                }
            """)
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)

            # Confirm button
            confirm_btn = QPushButton("Ha, davom etish")
            confirm_btn.setMinimumHeight(38)
            confirm_btn.setCursor(Qt.PointingHandCursor)
            confirm_btn.setStyleSheet("""
                QPushButton {
                    background-color: #38BDF8;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0 20px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #0EA5E9;
                }
            """)
            confirm_btn.clicked.connect(self.accept)
            button_layout.addWidget(confirm_btn)
        else:
            # OK button
            ok_btn = QPushButton("OK")
            ok_btn.setMinimumHeight(38)
            ok_btn.setMinimumWidth(100)
            ok_btn.setCursor(Qt.PointingHandCursor)
            ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #38BDF8;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 0 20px;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #0EA5E9;
                }
            """)
            ok_btn.clicked.connect(self.accept)
            button_layout.addWidget(ok_btn)

        container.addLayout(button_layout)

        # Apply container style
        container_widget = QLabel()
        container_widget.setLayout(container)
        container_widget.setStyleSheet("""
            QLabel {
                background-color: #111827;
                border: 1px solid #334155;
                border-radius: 14px;
            }
        """)

        main_layout.addWidget(container_widget)
        self.setLayout(main_layout)

    def setup_animation(self):
        """Setup fade-in animation"""
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(120)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def get_icon(self):
        """Get icon based on alert type"""
        icons = {
            self.SUCCESS: "✓",
            self.ERROR: "✕",
            self.WARNING: "⚠",
            self.INFO: "ℹ",
            self.CONFIRM: "?",
        }
        return icons.get(self.alert_type, "ℹ")

    def get_icon_color(self):
        """Get icon color based on alert type"""
        colors = {
            self.SUCCESS: "#22c55e",
            self.ERROR: "#ef4444",
            self.WARNING: "#f59e0b",
            self.INFO: "#3b82f6",
            self.CONFIRM: "#f59e0b",
        }
        return colors.get(self.alert_type, "#3b82f6")

    @staticmethod
    def show_success(parent=None, title="Muvaffaqiyat", message=""):
        """Show success alert"""
        dialog = CustomAlert(parent, CustomAlert.SUCCESS, title, message)
        dialog.exec()

    @staticmethod
    def show_error(parent=None, title="Xato", message=""):
        """Show error alert"""
        dialog = CustomAlert(parent, CustomAlert.ERROR, title, message)
        dialog.exec()

    @staticmethod
    def show_warning(parent=None, title="Ogohlantirish", message=""):
        """Show warning alert"""
        dialog = CustomAlert(parent, CustomAlert.WARNING, title, message)
        dialog.exec()

    @staticmethod
    def show_info(parent=None, title="Ma'lumot", message=""):
        """Show info alert"""
        dialog = CustomAlert(parent, CustomAlert.INFO, title, message)
        dialog.exec()

    @staticmethod
    def show_confirm(parent=None, title="Tasdiqlash", message=""):
        """Show confirm dialog, returns True if confirmed"""
        dialog = CustomAlert(parent, CustomAlert.CONFIRM, title, message)
        return dialog.exec() == QDialog.Accepted
