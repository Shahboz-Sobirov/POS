# -*- coding: utf-8 -*-
"""
Reports Page (F4)
Daily, Weekly, Monthly, Yearly, Custom Range
"""
from html import escape
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QComboBox, QDateEdit, QGroupBox,
                               QFileDialog)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QShortcut, QKeySequence, QTextDocument
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrinterInfo
from openpyxl import Workbook
from openpyxl.styles import Font
from services.sale_service import SaleService
from widgets.custom_alert import CustomAlert
from utils.error_logger import log_exception, get_user_friendly_message


class ReportsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.current_sales = []
        self.current_start_datetime = None
        self.current_end_datetime = None
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Title
        title = QLabel("Hisobotlar")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Filter section
        filter_group = QGroupBox("Filtr")
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)

        # Mode selector
        mode_label = QLabel("Davr:")
        filter_layout.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.setMinimumHeight(40)
        self.mode_combo.addItem("Kunlik", "daily")
        self.mode_combo.addItem("Haftalik", "weekly")
        self.mode_combo.addItem("Oylik", "monthly")
        self.mode_combo.addItem("Yillik", "yearly")
        self.mode_combo.addItem("Maxsus", "custom")
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        filter_layout.addWidget(self.mode_combo)

        # Date range with custom styling
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setMinimumHeight(40)
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        self.apply_date_style(self.start_date)
        filter_layout.addWidget(self.start_date)

        range_label = QLabel("-")
        filter_layout.addWidget(range_label)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumHeight(40)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        self.end_date.setEnabled(False)  # Enabled only in custom mode
        self.apply_date_style(self.end_date)
        filter_layout.addWidget(self.end_date)

        # Load button
        load_btn = QPushButton("📊 Yuklash")
        load_btn.setObjectName("btnSuccess")
        load_btn.setMinimumHeight(40)
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.clicked.connect(self.load_report)
        filter_layout.addWidget(load_btn)

        # Print button
        print_btn = QPushButton("🖨️ Chop Etish")
        print_btn.setMinimumHeight(40)
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.clicked.connect(self.print_report)
        filter_layout.addWidget(print_btn)

        # Excel button
        excel_btn = QPushButton("📑 Excel")
        excel_btn.setMinimumHeight(40)
        excel_btn.setCursor(Qt.PointingHandCursor)
        excel_btn.clicked.connect(self.export_excel)
        filter_layout.addWidget(excel_btn)

        filter_layout.addStretch()

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Summary section
        summary_group = QGroupBox("Umumiy Ma'lumot")
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(16)

        # Total sales
        self.total_sales_label = QLabel("Savdolar: 0")
        self.total_sales_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        summary_layout.addWidget(self.total_sales_label)

        # Total revenue
        self.total_revenue_label = QLabel("Daromad: 0 so'm")
        self.total_revenue_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #3498db;")
        summary_layout.addWidget(self.total_revenue_label)

        # Total profit
        self.total_profit_label = QLabel("Foyda: 0 so'm")
        self.total_profit_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #27ae60;")
        summary_layout.addWidget(self.total_profit_label)

        summary_layout.addStretch()

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Payment breakdown
        payment_group = QGroupBox("To'lovlar Taqsimoti")
        payment_layout = QHBoxLayout()
        payment_layout.setSpacing(16)

        self.naqd_label = QLabel("💵 Naqd: 0")
        payment_layout.addWidget(self.naqd_label)

        self.karta_label = QLabel("💳 Karta: 0")
        payment_layout.addWidget(self.karta_label)

        self.click_label = QLabel("📱 Click: 0")
        payment_layout.addWidget(self.click_label)

        self.qarz_label = QLabel("📋 Qarz: 0")
        payment_layout.addWidget(self.qarz_label)

        payment_layout.addStretch()

        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Sana", "Mijoz", "Mahsulotlar", "To'lov", "Summa", "Foyda"
        ])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)
        layout.addWidget(self.table)

        self.setLayout(layout)

        # Load default (daily)
        self.load_report()

    def setup_shortcuts(self):
        """Setup shortcuts"""
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self.print_report)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.export_excel)

    def on_mode_changed(self):
        """Mode changed"""
        mode = self.mode_combo.currentData()
        self.end_date.setEnabled(mode == "custom")

        if mode == "custom":
            if self.end_date.date() < self.start_date.date():
                self.end_date.setDate(self.start_date.date())
            return

        today = datetime.now().date()
        if mode == "daily":
            start_date = today
            end_date = today
        elif mode == "weekly":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif mode == "monthly":
            start_date = today.replace(day=1)
            next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_date = next_month - timedelta(days=1)
        else:
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)

        self.start_date.setDate(QDate(start_date.year, start_date.month, start_date.day))
        self.end_date.setDate(QDate(end_date.year, end_date.month, end_date.day))
        self.load_report()

    def get_date_range(self):
        """Resolve current date range based on selected mode"""
        mode = self.mode_combo.currentData()
        start_date = self.start_date.date().toPython()

        if mode == "custom":
            end_date = self.end_date.date().toPython()
            if end_date < start_date:
                raise ValueError("Tugash sanasi boshlanish sanasidan kichik bo'lishi mumkin emas")
        elif mode == "daily":
            end_date = start_date
        elif mode == "weekly":
            end_date = start_date + timedelta(days=6)
        elif mode == "monthly":
            next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_date = next_month - timedelta(days=1)
        else:
            end_date = start_date.replace(month=12, day=31)

        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        return start_datetime, end_datetime

    def load_report(self):
        """Load report"""
        try:
            start_datetime, end_datetime = self.get_date_range()

            # Get sales
            sales = SaleService.get_by_date_range(start_datetime, end_datetime)
            self.current_sales = sales
            self.current_start_datetime = start_datetime
            self.current_end_datetime = end_datetime

            # Calculate totals
            total_sales = len(sales)
            total_revenue = sum(s.total_amount for s in sales)
            total_profit = sum(s.profit for s in sales)

            # Payment breakdown
            payment_totals = {'naqd': 0, 'karta': 0, 'click': 0, 'qarz': 0}
            for sale in sales:
                if sale.payment_breakdown:
                    for key, value in sale.payment_breakdown.items():
                        if key in payment_totals:
                            payment_totals[key] += value

            # Update summary
            self.total_sales_label.setText(f"Savdolar: {total_sales}")
            self.total_revenue_label.setText(f"Daromad: {total_revenue:,.0f} so'm")
            self.total_profit_label.setText(f"Foyda: {total_profit:,.0f} so'm")

            # Update payment breakdown
            self.naqd_label.setText(f"💵 Naqd: {payment_totals['naqd']:,.0f}")
            self.karta_label.setText(f"💳 Karta: {payment_totals['karta']:,.0f}")
            self.click_label.setText(f"📱 Click: {payment_totals['click']:,.0f}")
            self.qarz_label.setText(f"📋 Qarz: {payment_totals['qarz']:,.0f}")

            # Populate table
            self.populate_table(sales)

        except Exception as e:
            log_exception(e, "load_report")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def populate_table(self, sales):
        """Populate table with safe rendering"""
        self.table.setRowCount(len(sales))

        for row, sale in enumerate(sales):
            try:
                # Date - SAFE
                try:
                    date_str = sale.sale_date.strftime("%d.%m.%Y %H:%M") if sale.sale_date else "-"
                except:
                    date_str = "-"
                self.table.setItem(row, 0, QTableWidgetItem(date_str))

                # Customer - SAFE
                try:
                    customer_name = sale.customer.full_name if sale.customer else "-"
                except:
                    customer_name = "-"
                self.table.setItem(row, 1, QTableWidgetItem(customer_name))

                # Products - SAFE
                try:
                    products_list = [item.product.name for item in sale.items if item.product]
                    if products_list:
                        products_str = ", ".join(products_list[:2])
                        if len(products_list) > 2:
                            products_str += f" (+{len(products_list) - 2})"
                    else:
                        products_str = "-"
                except:
                    products_str = "-"
                self.table.setItem(row, 2, QTableWidgetItem(products_str))

                # Payment - SAFE
                try:
                    payment_str = self.format_payment_breakdown(sale.payment_breakdown)
                except:
                    payment_str = "-"
                self.table.setItem(row, 3, QTableWidgetItem(payment_str))

                # Amount - SAFE
                try:
                    amount_str = f"{sale.total_amount:,.0f}" if sale.total_amount else "0"
                except:
                    amount_str = "0"
                self.table.setItem(row, 4, QTableWidgetItem(amount_str))

                # Profit - SAFE
                try:
                    profit_str = f"{sale.profit:,.0f}" if sale.profit else "0"
                except:
                    profit_str = "0"
                self.table.setItem(row, 5, QTableWidgetItem(profit_str))

            except Exception as e:
                # If entire row fails, log and skip
                print(f"Warning: Failed to render sale row {row}: {e}")
                # Fill with placeholder data
                for col in range(6):
                    self.table.setItem(row, col, QTableWidgetItem("-"))

    def format_payment_breakdown(self, breakdown):
        """Format payment breakdown - NO 'Mixed'"""
        if not breakdown:
            return "Naqd"

        parts = []
        if breakdown.get('naqd', 0) > 0:
            parts.append(f"Naqd: {breakdown['naqd']:,.0f}")
        if breakdown.get('karta', 0) > 0:
            parts.append(f"Karta: {breakdown['karta']:,.0f}")
        if breakdown.get('click', 0) > 0:
            parts.append(f"Click: {breakdown['click']:,.0f}")
        if breakdown.get('qarz', 0) > 0:
            parts.append(f"Qarz: {breakdown['qarz']:,.0f}")

        return "\n".join(parts) if parts else "Naqd"

    def get_products_summary(self, sale):
        """Get compact product list for UI/export/printing"""
        products_list = [item.product.name for item in sale.items if item.product]
        if not products_list:
            return "-"
        if len(products_list) <= 2:
            return ", ".join(products_list)
        return f"{', '.join(products_list[:2])} (+{len(products_list) - 2})"

    def build_report_html(self):
        """Build printable HTML from the currently loaded report"""
        total_revenue = sum(s.total_amount for s in self.current_sales)
        total_profit = sum(s.profit for s in self.current_sales)

        rows = []
        for sale in self.current_sales:
            customer_name = sale.customer.full_name if sale.customer else "-"
            rows.append(
                f"""
                <tr>
                    <td>{escape(sale.sale_date.strftime("%d.%m.%Y %H:%M"))}</td>
                    <td>{escape(customer_name)}</td>
                    <td>{escape(self.get_products_summary(sale))}</td>
                    <td>{escape(self.format_payment_breakdown(sale.payment_breakdown)).replace(chr(10), "<br>")}</td>
                    <td style="text-align:right;">{sale.total_amount:,.0f}</td>
                    <td style="text-align:right;">{sale.profit:,.0f}</td>
                </tr>
                """
            )

        date_range = (
            f"{self.current_start_datetime.strftime('%d.%m.%Y')} - "
            f"{self.current_end_datetime.strftime('%d.%m.%Y')}"
        )

        return f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 12px; color: #111827; }}
                h1 {{ font-size: 20px; margin-bottom: 4px; }}
                p {{ margin: 4px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
                th, td {{ border: 1px solid #CBD5E1; padding: 8px; vertical-align: top; }}
                th {{ background: #E2E8F0; text-align: left; }}
                .summary {{ margin-top: 12px; }}
            </style>
        </head>
        <body>
            <h1>Profel Savdo Hisoboti</h1>
            <p>Davr: {escape(date_range)}</p>
            <div class="summary">
                <p>Savdolar: {len(self.current_sales)}</p>
                <p>Daromad: {total_revenue:,.0f} so'm</p>
                <p>Foyda: {total_profit:,.0f} so'm</p>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Sana</th>
                        <th>Mijoz</th>
                        <th>Mahsulotlar</th>
                        <th>To'lov</th>
                        <th>Summa</th>
                        <th>Foyda</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </body>
        </html>
        """

    def print_report(self):
        """Print report (CTRL+P)"""
        if not self.current_sales:
            CustomAlert.show_warning(self, "Ogohlantirish", "Chop etish uchun hisobot bo'sh")
            return

        if not self.check_printer_available():
            CustomAlert.show_warning(self, "Ogohlantirish", "Printer topilmadi")
            return

        try:
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            if not dialog.exec():
                return

            document = QTextDocument()
            document.setHtml(self.build_report_html())
            document.print(printer)
            CustomAlert.show_success(self, "Muvaffaqiyat", "Hisobot printerga yuborildi")
        except Exception as e:
            log_exception(e, "print_report")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def check_printer_available(self):
        """Check if printer is available"""
        try:
            default_printer = QPrinterInfo.defaultPrinter()
            return not default_printer.isNull()
        except Exception:
            return False

    def export_excel(self):
        """Export to Excel (CTRL+E)"""
        if not self.current_sales:
            CustomAlert.show_warning(self, "Ogohlantirish", "Export qilish uchun hisobot bo'sh")
            return

        default_name = (
            f"hisobot_{self.current_start_datetime.strftime('%Y%m%d')}_"
            f"{self.current_end_datetime.strftime('%Y%m%d')}.xlsx"
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Excel faylni saqlash",
            default_name,
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        try:
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Hisobot"

            sheet["A1"] = "Profel Savdo Hisoboti"
            sheet["A1"].font = Font(bold=True, size=14)
            sheet["A2"] = "Davr"
            sheet["B2"] = (
                f"{self.current_start_datetime.strftime('%d.%m.%Y')} - "
                f"{self.current_end_datetime.strftime('%d.%m.%Y')}"
            )
            sheet["A3"] = "Savdolar"
            sheet["B3"] = len(self.current_sales)
            sheet["A4"] = "Daromad"
            sheet["B4"] = sum(s.total_amount for s in self.current_sales)
            sheet["A5"] = "Foyda"
            sheet["B5"] = sum(s.profit for s in self.current_sales)

            header_row = 7
            headers = ["Sana", "Mijoz", "Mahsulotlar", "To'lov", "Summa", "Foyda"]
            for column, header in enumerate(headers, start=1):
                cell = sheet.cell(row=header_row, column=column, value=header)
                cell.font = Font(bold=True)

            for row_index, sale in enumerate(self.current_sales, start=header_row + 1):
                customer_name = sale.customer.full_name if sale.customer else "-"
                sheet.cell(row=row_index, column=1, value=sale.sale_date.strftime("%d.%m.%Y %H:%M"))
                sheet.cell(row=row_index, column=2, value=customer_name)
                sheet.cell(row=row_index, column=3, value=self.get_products_summary(sale))
                sheet.cell(row=row_index, column=4, value=self.format_payment_breakdown(sale.payment_breakdown))
                sheet.cell(row=row_index, column=5, value=sale.total_amount)
                sheet.cell(row=row_index, column=6, value=sale.profit)

            sheet.freeze_panes = "A8"
            sheet.column_dimensions["A"].width = 18
            sheet.column_dimensions["B"].width = 24
            sheet.column_dimensions["C"].width = 34
            sheet.column_dimensions["D"].width = 28
            sheet.column_dimensions["E"].width = 16
            sheet.column_dimensions["F"].width = 16

            workbook.save(file_path)
            CustomAlert.show_success(self, "Muvaffaqiyat", f"Excel fayl saqlandi:\n{file_path}")
        except Exception as e:
            log_exception(e, "export_excel")
            CustomAlert.show_error(self, "Xato", get_user_friendly_message(e))

    def refresh(self):
        """Refresh page"""
        self.load_report()

    def apply_date_style(self, date_edit):
        """Apply custom style to QDateEdit and QCalendarWidget"""
        date_edit.setStyleSheet("""
            QDateEdit {
                background-color: white;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding-left: 10px;
                color: #0F172A;
                font-size: 13px;
            }
            QDateEdit:hover {
                border: 1px solid #38BDF8;
            }
            QDateEdit:focus {
                border: 2px solid #38BDF8;
            }
            QDateEdit:disabled {
                background-color: #F1F5F9;
                color: #94A3B8;
            }
            QDateEdit::drop-down {
                border: none;
                width: 30px;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #0F172A;
                margin-right: 8px;
            }
            QDateEdit:disabled::down-arrow {
                border-top-color: #94A3B8;
            }

            /* Calendar Widget */
            QCalendarWidget {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
            }
            QCalendarWidget QToolButton {
                background-color: transparent;
                color: #0F172A;
                border-radius: 4px;
                padding: 4px;
                font-weight: 600;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #E0F2FE;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #CBD5E1;
                color: #0F172A;
            }
            QCalendarWidget QSpinBox {
                background-color: white;
                border: 1px solid #CBD5E1;
                border-radius: 4px;
                padding: 4px;
                color: #0F172A;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #082F49;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QCalendarWidget QWidget {
                color: #0F172A;
            }
            QCalendarWidget QAbstractItemView {
                background-color: white;
                selection-background-color: #38BDF8;
                selection-color: white;
                color: #0F172A;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #0F172A;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #94A3B8;
            }
        """)
