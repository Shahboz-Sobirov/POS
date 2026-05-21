# -*- coding: utf-8 -*-
"""
Startup lock panel shown before the main window opens.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LockPanel(QDialog):
    """Simple password gate for the application."""

    PASSWORD = "6660"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LockPanel")
        self.setModal(True)
        self.setFixedSize(420, 240)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("LockPanel")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: 700; color: #0F172A;")
        layout.addWidget(title)

        subtitle = QLabel("Dasturga kirish uchun parolni kiriting")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #475569;")
        layout.addWidget(subtitle)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Parol")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(44)
        self.password_input.returnPressed.connect(self.validate_password)
        self.password_input.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid #CBD5E1;
                border-radius: 10px;
                padding: 0 14px;
                font-size: 16px;
                background: white;
                color: #0F172A;
            }
            QLineEdit:focus {
                border: 2px solid #38BDF8;
            }
            """
        )
        layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("font-size: 12px; color: #DC2626;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        cancel_button = QPushButton("Bekor qilish")
        cancel_button.setMinimumHeight(42)
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)

        unlock_button = QPushButton("Kirish")
        unlock_button.setMinimumHeight(42)
        unlock_button.clicked.connect(self.validate_password)
        unlock_button.setStyleSheet(
            """
            QPushButton {
                background: #0F766E;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 18px;
            }
            QPushButton:hover {
                background: #115E59;
            }
            """
        )
        button_row.addWidget(unlock_button)

        layout.addLayout(button_row)

        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("background: #F8FAFC; border-radius: 14px;")

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(container)
        self.setLayout(root_layout)

        self.password_input.setFocus()

    def validate_password(self):
        """Unlock app only when the configured password is entered."""
        if self.password_input.text().strip() == self.PASSWORD:
            self.accept()
            return

        self.error_label.setText("Parol noto'g'ri. Qayta urinib ko'ring.")
        self.error_label.setVisible(True)
        self.password_input.clear()
        self.password_input.setFocus()
