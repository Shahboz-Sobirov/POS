# -*- coding: utf-8 -*-
"""
Production-style thermal receipt printing demo for PySide6.

Features:
- 58mm and 80mm thermal printer support
- HTML/CSS receipt rendering via QTextDocument
- Auto page height based on rendered content
- Print preview support
- Direct print support
- High-resolution thermal-friendly layout
"""
from __future__ import annotations

import html
import math
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Literal

from PySide6.QtCore import QMarginsF, QSizeF, Qt
from PySide6.QtGui import QAction, QFont, QTextDocument
from PySide6.QtPrintSupport import QPrintPreviewDialog, QPrinter, QPrinterInfo
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


ThermalPaperWidth = Literal["58mm", "80mm"]


@dataclass(slots=True)
class ReceiptItem:
    """Single line item on the receipt."""

    name: str
    qty: float
    unit: str
    price: float

    @property
    def subtotal(self) -> float:
        return self.qty * self.price


@dataclass(slots=True)
class ReceiptData:
    """Normalized receipt payload."""

    store_name: str
    address: str
    phone: str
    cashier: str
    receipt_no: str
    created_at: datetime
    payment_type: str
    items: list[ReceiptItem] = field(default_factory=list)
    thank_you_text: str = "Xaridingiz uchun rahmat!"
    footer_note: str = "Yana kutib qolamiz!"
    currency: str = "so'm"
    amount_paid: float = 0.0

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)

    @property
    def change_amount(self) -> float:
        return max(0.0, self.amount_paid - self.total)


class ReceiptPrinter:
    """
    Professional thermal receipt engine.

    Rendering flow:
    1. Build semantic HTML via `generate_html()`
    2. Create QTextDocument with thermal-friendly CSS
    3. Measure content height using a temporary large page
    4. Rebuild printer page size with exact content height
    5. Print/preview with QPrintPreviewDialog or direct print
    """

    PAPER_WIDTH_MM = {
        "58mm": 58.0,
        "80mm": 80.0,
    }
    PAPER_NAME = {
        "58mm": "Thermal58mm",
        "80mm": "Thermal80mm",
    }

    # Small margins help avoid printer non-printable-area clipping.
    PAGE_MARGINS_MM = QMarginsF(2.0, 2.0, 2.0, 2.0)
    MIN_PAGE_HEIGHT_MM = 70.0
    MAX_PAGE_HEIGHT_MM = 800.0
    PREVIEW_ZOOM = 1.25

    def __init__(self, paper_width: ThermalPaperWidth = "80mm") -> None:
        if paper_width not in self.PAPER_WIDTH_MM:
            raise ValueError(f"Unsupported paper width: {paper_width}")
        self.paper_width = paper_width

    @staticmethod
    def is_printer_available() -> bool:
        """Return True when a default printer exists."""
        try:
            return not QPrinterInfo.defaultPrinter().isNull()
        except Exception:
            return False

    def generate_html(self, receipt: ReceiptData) -> str:
        """Generate professional thermal-receipt HTML."""
        width_mm = self.PAPER_WIDTH_MM[self.paper_width]
        is_narrow = width_mm <= 58.0

        base_font = 8 if is_narrow else 9
        title_font = 11 if is_narrow else 13
        total_font = 10 if is_narrow else 12

        item_rows = "".join(self._build_item_row(item) for item in receipt.items)
        if not item_rows:
            item_rows = (
                '<tr><td colspan="4" class="empty-row">Mahsulot mavjud emas</td></tr>'
            )

        payment_label = self._escape(receipt.payment_type)
        created_at = receipt.created_at.strftime("%d.%m.%Y %H:%M:%S")

        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    @page {{
      margin: 0;
    }}

    html, body {{
      margin: 0;
      padding: 0;
      background: #ffffff;
      color: #111111;
      font-family: "Consolas", "Courier New", monospace;
      font-size: {base_font}pt;
      line-height: 1.28;
    }}

    .receipt {{
      width: 100%;
      box-sizing: border-box;
      padding: 0;
    }}

    .center {{
      text-align: center;
    }}

    .store-title {{
      font-size: {title_font}pt;
      font-weight: 700;
      letter-spacing: 0.4px;
      margin: 0 0 2mm 0;
      text-transform: uppercase;
    }}

    .meta,
    .footer {{
      margin: 0;
    }}

    .muted {{
      color: #333333;
    }}

    .separator {{
      margin: 2.2mm 0;
      color: #111111;
      white-space: nowrap;
      overflow: hidden;
      font-size: {base_font}pt;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }}

    .items th,
    .items td {{
      padding: 0.8mm 0;
      vertical-align: top;
      word-wrap: break-word;
    }}

    .items th {{
      font-weight: 700;
      border-bottom: 0.35mm dashed #111111;
      padding-bottom: 1.2mm;
    }}

    .items .col-name {{
      width: 46%;
      text-align: left;
      padding-right: 1.2mm;
    }}

    .items .col-qty {{
      width: 18%;
      text-align: right;
      padding-right: 1.2mm;
    }}

    .items .col-price {{
      width: 18%;
      text-align: right;
      padding-right: 1.2mm;
    }}

    .items .col-subtotal {{
      width: 18%;
      text-align: right;
    }}

    .summary {{
      margin-top: 1.2mm;
    }}

    .summary-row {{
      width: 100%;
      margin: 0.6mm 0;
      overflow: hidden;
    }}

    .summary-label {{
      float: left;
      max-width: 58%;
    }}

    .summary-value {{
      float: right;
      text-align: right;
      max-width: 42%;
    }}

    .summary-row::after {{
      content: "";
      display: block;
      clear: both;
    }}

    .total-box {{
      margin-top: 2mm;
      padding-top: 1.2mm;
      border-top: 0.45mm solid #111111;
      font-size: {total_font}pt;
      font-weight: 700;
    }}

    .empty-row {{
      text-align: center;
      padding: 2mm 0;
      color: #444444;
    }}
  </style>
</head>
<body>
  <div class="receipt">
    <div class="center">
      <div class="store-title">{self._escape(receipt.store_name)}</div>
      <p class="meta muted">{self._escape(receipt.address)}</p>
      <p class="meta muted">Tel: {self._escape(receipt.phone)}</p>
    </div>

    <div class="separator">{"-" * 80}</div>

    <div class="summary">
      <div class="summary-row">
        <span class="summary-label">Chek raqami</span>
        <span class="summary-value">{self._escape(receipt.receipt_no)}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Sana</span>
        <span class="summary-value">{self._escape(created_at)}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Kassir</span>
        <span class="summary-value">{self._escape(receipt.cashier)}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">To'lov turi</span>
        <span class="summary-value">{payment_label}</span>
      </div>
    </div>

    <div class="separator">{"-" * 80}</div>

    <table class="items">
      <thead>
        <tr>
          <th class="col-name">Mahsulot</th>
          <th class="col-qty">Soni</th>
          <th class="col-price">Narx</th>
          <th class="col-subtotal">Jami</th>
        </tr>
      </thead>
      <tbody>
        {item_rows}
      </tbody>
    </table>

    <div class="separator">{"-" * 80}</div>

    <div class="summary">
      <div class="summary-row total-box">
        <span class="summary-label">UMUMIY</span>
        <span class="summary-value">{self._money(receipt.total, receipt.currency)}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">To'langan</span>
        <span class="summary-value">{self._money(receipt.amount_paid, receipt.currency)}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">Qaytim</span>
        <span class="summary-value">{self._money(receipt.change_amount, receipt.currency)}</span>
      </div>
    </div>

    <div class="separator">{"-" * 80}</div>

    <div class="center footer">
      <p>{self._escape(receipt.thank_you_text)}</p>
      <p class="muted">{self._escape(receipt.footer_note)}</p>
    </div>
  </div>
</body>
</html>
"""

    def preview_receipt(self, receipt: ReceiptData, parent: QWidget | None = None) -> None:
        """Open QPrintPreviewDialog with exact thermal page layout."""
        printer = self._create_printer()
        preview = QPrintPreviewDialog(printer, parent)
        preview.setWindowTitle(f"Receipt Preview ({self.paper_width})")
        preview.setMinimumSize(960, 720)
        preview.setZoomFactor(self.PREVIEW_ZOOM)
        preview.paintRequested.connect(lambda p: self._render_receipt(receipt, p))
        preview.exec()

    def print_receipt(self, receipt: ReceiptData, printer: QPrinter | None = None) -> None:
        """Print receipt directly to the given or default printer."""
        target_printer = printer or self._create_printer()
        self._render_receipt(receipt, target_printer)

    def _build_item_row(self, item: ReceiptItem) -> str:
        qty_text = self._escape(self._format_qty(item.qty, item.unit))
        price_text = self._escape(self._money(item.price, None))
        subtotal_text = self._escape(self._money(item.subtotal, None))
        return f"""
        <tr>
          <td class="col-name">{self._escape(item.name)}</td>
          <td class="col-qty">{qty_text}</td>
          <td class="col-price">{price_text}</td>
          <td class="col-subtotal">{subtotal_text}</td>
        </tr>
        """

    def _render_receipt(self, receipt: ReceiptData, printer: QPrinter) -> None:
        """Full render pipeline with auto-height thermal page sizing."""
        html_content = self.generate_html(receipt)

        provisional_printer = self._create_printer()
        provisional_printer.setPrinterName(printer.printerName())
        initial_layout = self._build_page_layout(
            width_mm=self.PAPER_WIDTH_MM[self.paper_width],
            height_mm=400.0,
        )
        provisional_printer.setPageLayout(initial_layout)

        document = self._create_document(html_content, provisional_printer)

        content_height_mm = self._calculate_content_height_mm(document, provisional_printer)
        final_height_mm = max(self.MIN_PAGE_HEIGHT_MM, min(content_height_mm, self.MAX_PAGE_HEIGHT_MM))
        final_layout = self._build_page_layout(
            width_mm=self.PAPER_WIDTH_MM[self.paper_width],
            height_mm=final_height_mm,
        )
        printer.setPageLayout(final_layout)
        printer.setResolution(provisional_printer.resolution())

        final_document = self._create_document(html_content, printer)
        final_document.print(printer)

    def _create_printer(self) -> QPrinter:
        """Create a high-resolution native printer."""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.NativeFormat)
        printer.setFullPage(False)
        printer.setResolution(203)
        return printer

    def _build_page_layout(self, width_mm: float, height_mm: float) -> QPageLayout:
        """Create a custom thermal page layout with exact width and auto height."""
        page_size = QPageSize(
            QSizeF(width_mm, height_mm),
            QPageSize.Unit.Millimeter,
            self.PAPER_NAME[self.paper_width],
        )
        layout = QPageLayout(
            page_size,
            QPageLayout.Portrait,
            self.PAGE_MARGINS_MM,
            QPageLayout.Unit.Millimeter,
        )
        return layout

    def _create_document(self, html_content: str, printer: QPrinter) -> QTextDocument:
        """Create and size QTextDocument to the printable width."""
        document = QTextDocument()
        document.setDefaultFont(QFont("Consolas", 9))
        document.setDocumentMargin(0)
        document.setHtml(html_content)

        printable_rect = printer.pageLayout().paintRectPixels(printer.resolution())
        document.setPageSize(QSizeF(float(printable_rect.width()), 100000.0))
        return document

    def _calculate_content_height_mm(self, document: QTextDocument, printer: QPrinter) -> float:
        """Convert rendered document height to millimeters for exact page sizing."""
        printable_rect = printer.pageLayout().paintRectPixels(printer.resolution())
        content_height_px = document.size().height()
        margin_top_mm = self.PAGE_MARGINS_MM.top()
        margin_bottom_mm = self.PAGE_MARGINS_MM.bottom()

        pixels_to_mm = 25.4 / printer.resolution()
        content_height_mm = content_height_px * pixels_to_mm

        # Add a small safety buffer so the footer is not clipped.
        return content_height_mm + margin_top_mm + margin_bottom_mm + 6.0

    @staticmethod
    def _format_qty(qty: float, unit: str) -> str:
        """Format quantity for the receipt table."""
        if unit.lower() in {"dona", "ta", "don", "pcs", "piece"}:
            return f"{int(qty)} {unit}"
        if math.isclose(qty, round(qty), abs_tol=1e-9):
            return f"{int(round(qty))} {unit}"
        return f"{qty:.2f}".rstrip("0").rstrip(".") + f" {unit}"

    @staticmethod
    def _money(amount: float, currency: str | None) -> str:
        """Money formatter for receipt output."""
        suffix = f" {currency}" if currency else ""
        return f"{amount:,.0f}{suffix}"

    @staticmethod
    def _escape(value: object) -> str:
        """HTML escape helper."""
        return html.escape(str(value))


class DemoWindow(QMainWindow):
    """Minimal demo UI for previewing and printing."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Thermal Receipt Printer Demo")
        self.resize(880, 500)

        self.receipt_data = self._build_sample_data()
        self.printer_58 = ReceiptPrinter("58mm")
        self.printer_80 = ReceiptPrinter("80mm")

        self._setup_ui()

    def _setup_ui(self) -> None:
        toolbar = QToolBar("Actions")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        action_preview_58 = QAction("Preview 58mm", self)
        action_preview_58.triggered.connect(lambda: self.printer_58.preview_receipt(self.receipt_data, self))
        toolbar.addAction(action_preview_58)

        action_preview_80 = QAction("Preview 80mm", self)
        action_preview_80.triggered.connect(lambda: self.printer_80.preview_receipt(self.receipt_data, self))
        toolbar.addAction(action_preview_80)

        action_print_80 = QAction("Direct Print 80mm", self)
        action_print_80.triggered.connect(self._print_80mm)
        toolbar.addAction(action_print_80)

        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Production-Ready Thermal Receipt Engine")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        description = QLabel(
            "HTML/CSS + QTextDocument + QPrinter asosidagi professional POS thermal receipt demo.\n"
            "58mm va 80mm preview'ni oching, keyin direct print orqali default printerga yuboring."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 14px; color: #334155;")
        layout.addWidget(description)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        btn_preview_58 = QPushButton("Preview 58mm")
        btn_preview_58.clicked.connect(lambda: self.printer_58.preview_receipt(self.receipt_data, self))
        buttons.addWidget(btn_preview_58)

        btn_preview_80 = QPushButton("Preview 80mm")
        btn_preview_80.clicked.connect(lambda: self.printer_80.preview_receipt(self.receipt_data, self))
        buttons.addWidget(btn_preview_80)

        btn_print_80 = QPushButton("Direct Print 80mm")
        btn_print_80.clicked.connect(self._print_80mm)
        buttons.addWidget(btn_print_80)

        layout.addLayout(buttons)
        layout.addStretch()

        central.setLayout(layout)
        self.setCentralWidget(central)

    def _print_80mm(self) -> None:
        if not ReceiptPrinter.is_printer_available():
            QMessageBox.warning(self, "Printer", "Default printer topilmadi.")
            return

        try:
            self.printer_80.print_receipt(self.receipt_data)
            QMessageBox.information(self, "Print", "Receipt printerga yuborildi.")
        except Exception as exc:
            QMessageBox.critical(self, "Print Error", str(exc))

    @staticmethod
    def _build_sample_data() -> ReceiptData:
        return ReceiptData(
            store_name="PROFEL SAVDO",
            address="Toshkent sh., Chilonzor tumani, 12-kvartal, 45-uy",
            phone="+998 90 123 45 67",
            cashier="Azizbek",
            receipt_no="PS-2026-000184",
            created_at=datetime.now(),
            payment_type="Naqd",
            amount_paid=300000,
            items=[
                ReceiptItem("Profil 60x40 Premium", 6, "dona", 18500),
                ReceiptItem("Ruchka Lux Model X", 2, "dona", 45000),
                ReceiptItem("Setka alyumin 1.8mm", 2.5, "metr", 22000),
                ReceiptItem("Qulf komplekt", 1, "dona", 78000),
            ],
            thank_you_text="Xaridingiz uchun rahmat!",
            footer_note="Savol va takliflar uchun biz bilan bog'laning.",
        )


def main() -> None:
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
