# -*- coding: utf-8 -*-
"""
Settings Page - Database Configuration
"""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QSpinBox,
    QGroupBox,
    QFormLayout,
)
from PySide6.QtCore import Qt

from models.base import reconnect_database
from utils.db_connection import get_db_connection, test_postgresql_connection
from widgets.custom_alert import CustomAlert


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db_conn = get_db_connection()
        self.setup_ui()
        self.load_current_settings()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Sozlamalar")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: 600; padding: 12px;")
        layout.addWidget(self.status_label)
        self.update_status_label()

        server_group = QGroupBox("Server Sozlamalari")
        server_layout = QFormLayout()
        server_layout.setSpacing(12)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("192.168.1.100")
        self.host_input.setMinimumHeight(40)
        server_layout.addRow("IP Manzil:", self.host_input)

        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(5432)
        self.port_input.setMinimumHeight(40)
        server_layout.addRow("Port:", self.port_input)

        self.database_input = QLineEdit()
        self.database_input.setPlaceholderText("profel_savdo")
        self.database_input.setMinimumHeight(40)
        server_layout.addRow("Database:", self.database_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("postgres")
        self.username_input.setMinimumHeight(40)
        server_layout.addRow("Foydalanuvchi:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Parol")
        self.password_input.setMinimumHeight(40)
        server_layout.addRow("Parol:", self.password_input)

        server_group.setLayout(server_layout)
        layout.addWidget(server_group)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        test_btn = QPushButton("Ulanishni Tekshirish")
        test_btn.setMinimumHeight(44)
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.clicked.connect(self.test_connection)
        btn_layout.addWidget(test_btn)

        save_btn = QPushButton("Saqlash va Ulash")
        save_btn.setObjectName("btnSuccess")
        save_btn.setMinimumHeight(44)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        use_sqlite_btn = QPushButton("SQLite Ishlatish")
        use_sqlite_btn.setMinimumHeight(44)
        use_sqlite_btn.setCursor(Qt.PointingHandCursor)
        use_sqlite_btn.clicked.connect(self.use_sqlite)
        btn_layout.addWidget(use_sqlite_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        info_group = QGroupBox("Ma'lumot")
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "Bu sahifa hozir ishlayotgan bazani ham ko'rsatadi.\n\n"
            "1. PostgreSQL ma'lumotlarini kiriting\n"
            "2. Ulanishni tekshiring\n"
            "3. Saqlash va Ulash tugmasini bosing\n"
            "4. Agar ulanish muvaffaqiyatli bo'lsa, baza shu zahoti almashadi\n\n"
            "Agar PostgreSQL ishlamasa, ilova SQLite fallback holatida qoladi."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #64748b; font-size: 12px; line-height: 1.6;")
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        self.setLayout(layout)

    def load_current_settings(self):
        """Load current database settings."""
        config = self.db_conn.config_manager.config
        self.host_input.setText(config.get("host", "localhost"))
        self.port_input.setValue(config.get("port", 5432))
        self.database_input.setText(config.get("database", "profel_savdo"))
        self.username_input.setText(config.get("username", "postgres"))
        self.password_input.setText(config.get("password", ""))

    def update_status_label(self):
        """Show the currently active database and fallback state."""
        conn_info = self.db_conn.get_connection_info()
        conn_type = conn_info["type"]
        config = conn_info["config"]
        configured_type = config.get("database_type", "sqlite")
        last_error = conn_info.get("last_error")

        if conn_type == "postgresql":
            self.status_label.setText(
                f"Faol baza: PostgreSQL | {config.get('host')}:{config.get('port')}/{config.get('database')}"
            )
            self.status_label.setStyleSheet(
                "font-size: 14px; font-weight: 600; padding: 12px; "
                "background-color: #d1fae5; color: #065f46; border-radius: 8px;"
            )
        elif conn_type == "sqlite":
            status_text = "Faol baza: SQLite (lokal)"
            if configured_type == "postgresql":
                status_text += "\nPostgreSQL ulanmagan, fallback ishlayapti."
                if last_error:
                    status_text += f"\nOxirgi xato: {last_error}"
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet(
                "font-size: 14px; font-weight: 600; padding: 12px; "
                "background-color: #dbeafe; color: #1e40af; border-radius: 8px;"
            )
        else:
            self.status_label.setText("Faol baza aniqlanmadi")
            self.status_label.setStyleSheet(
                "font-size: 14px; font-weight: 600; padding: 12px; "
                "background-color: #fee2e2; color: #991b1b; border-radius: 8px;"
            )

    def test_connection(self):
        """Test PostgreSQL connection."""
        host = self.host_input.text().strip()
        port = self.port_input.value()
        database = self.database_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not host or not database or not username:
            CustomAlert.show_warning(
                self,
                "Ogohlantirish",
                "IP manzil, database va foydalanuvchi nomini kiriting!",
            )
            return

        success, message = test_postgresql_connection(
            host, port, database, username, password
        )

        if success:
            CustomAlert.show_success(
                self,
                "Muvaffaqiyat",
                f"Server bilan ulanish muvaffaqiyatli!\n\n"
                f"Server: {host}:{port}\n"
                f"Database: {database}\n\n"
                f"Endi 'Saqlash va Ulash' tugmasini bosing.",
            )
        else:
            CustomAlert.show_error(
                self,
                "Ulanish Xatosi",
                f"{message}\n\n"
                f"Quyidagilarni tekshiring:\n"
                f"- PostgreSQL server ishga tushganmi?\n"
                f"- IP manzil to'g'rimi?\n"
                f"- Firewall ochiqmi?\n"
                f"- PostgreSQL LAN ulanishga ruxsat beradimi?",
            )

    def save_settings(self):
        """Save PostgreSQL settings and switch immediately."""
        host = self.host_input.text().strip()
        port = self.port_input.value()
        database = self.database_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not host or not database or not username:
            CustomAlert.show_warning(
                self,
                "Ogohlantirish",
                "Barcha majburiy maydonlarni to'ldiring!",
            )
            return

        success, message = test_postgresql_connection(
            host, port, database, username, password
        )
        if not success:
            CustomAlert.show_error(
                self,
                "Ulanish Xatosi",
                f"{message}\n\nAvval server ulanishini to'g'rilang, keyin saqlang.",
            )
            return

        new_config = {
            "database_type": "postgresql",
            "host": host,
            "port": port,
            "database": database,
            "username": username,
            "password": password,
            "fallback_to_sqlite": True,
            "sqlite_file": "profel_savdo.db",
        }

        if not self.db_conn.config_manager.save_config(new_config):
            CustomAlert.show_error(
                self,
                "Xato",
                "Sozlamalarni saqlashda xatolik yuz berdi!",
            )
            return

        success, conn_type = reconnect_database()
        self.update_status_label()
        if success:
            CustomAlert.show_success(
                self,
                "Muvaffaqiyat",
                "Sozlamalar saqlandi va shu zahoti qo'llandi.\n\n"
                f"Faol baza: {conn_type.upper()}",
            )
        else:
            CustomAlert.show_error(
                self,
                "Xato",
                f"Sozlamalar saqlandi, lekin ulanishni almashtirib bo'lmadi.\n\n{conn_type}",
            )

    def use_sqlite(self):
        """Switch to SQLite mode and apply immediately."""
        if not CustomAlert.show_confirm(
            self,
            "Tasdiqlash",
            "SQLite (lokal) rejimiga o'tmoqchimisiz?\n\n"
            "Bu rejimda faqat bitta kompyuter ishlatiladi.",
        ):
            return

        new_config = {
            "database_type": "sqlite",
            "fallback_to_sqlite": True,
            "sqlite_file": "profel_savdo.db",
        }

        if not self.db_conn.config_manager.save_config(new_config):
            CustomAlert.show_error(
                self,
                "Xato",
                "Sozlamalarni saqlashda xatolik!",
            )
            return

        success, conn_type = reconnect_database()
        self.update_status_label()
        if success:
            CustomAlert.show_success(
                self,
                "Muvaffaqiyat",
                "SQLite rejimiga o'tildi va shu zahoti qo'llandi.\n\n"
                f"Faol baza: {conn_type.upper()}",
            )
        else:
            CustomAlert.show_error(
                self,
                "Xato",
                f"SQLite rejimiga o'tishda xatolik.\n\n{conn_type}",
            )

    def refresh(self):
        """Refresh page."""
        self.load_current_settings()
        self.update_status_label()
