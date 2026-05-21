# -*- coding: utf-8 -*-
"""
Receipt printing via crisp A4 PDF invoice rendering.

This keeps the existing app-facing API stable while restoring the
ReportLab-based invoice layout that prints more clearly on standard paper.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from datetime import datetime
from types import SimpleNamespace

from PySide6.QtCore import QRectF
from PySide6.QtGui import QAction, QPainter, QPageLayout, QPageSize
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtPrintSupport import QPrinter, QPrinterInfo
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QToolBar,
    QVBoxLayout,
)

from reports.pdf_generator import PDFGenerator


class PdfPreviewDialog(QDialog):
    """Simple high-clarity PDF preview window."""

    def __init__(self, pdf_path: str, parent=None) -> None:
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.document = QPdfDocument(self)
        self.setWindowTitle("Hisob-Chek Preview")
        self.resize(1120, 820)
        self._setup_ui()

        status = self.document.load(self.pdf_path)
        if status != QPdfDocument.Error.None_:
            raise RuntimeError(f"PDF yuklanmadi: {status}")

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        toolbar = QToolBar()
        toolbar.setMovable(False)

        zoom_in = QAction("Kattalashtirish", self)
        zoom_in.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in)

        zoom_out = QAction("Kichiklashtirish", self)
        zoom_out.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out)

        fit_width = QAction("Eniga Sig'dirish", self)
        fit_width.triggered.connect(self.fit_width)
        toolbar.addAction(fit_width)

        fit_page = QAction("Sahifaga Sig'dirish", self)
        fit_page.triggered.connect(self.fit_page)
        toolbar.addAction(fit_page)

        layout.addWidget(toolbar)

        self.pdf_view = QPdfView()
        self.pdf_view.setDocument(self.document)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        layout.addWidget(self.pdf_view)

        button_layout = QHBoxLayout()
        print_btn = QPushButton("Chop Etish")
        print_btn.clicked.connect(self.print_pdf)
        button_layout.addWidget(print_btn)

        export_btn = QPushButton("Eksport PDF")
        export_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(export_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Yopish")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def zoom_in(self) -> None:
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self.pdf_view.setZoomFactor(self.pdf_view.zoomFactor() * 1.15)

    def zoom_out(self) -> None:
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self.pdf_view.setZoomFactor(max(0.2, self.pdf_view.zoomFactor() / 1.15))

    def fit_width(self) -> None:
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

    def fit_page(self) -> None:
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)

    def print_pdf(self) -> None:
        try:
            ReceiptPrinter.print_pdf_file(self.pdf_path)
            QMessageBox.information(self, "Muvaffaqiyat", "Chek printerga yuborildi.")
        except Exception as exc:
            QMessageBox.warning(self, "Printer xatosi", str(exc))

    def export_pdf(self) -> None:
        suggested_name = f"hisob-chek-preview-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        export_path, _ = QFileDialog.getSaveFileName(
            self,
            "Preview PDF saqlash",
            suggested_name,
            "PDF Files (*.pdf)"
        )
        if not export_path:
            return

        try:
            shutil.copyfile(self.pdf_path, export_path)
            QMessageBox.information(self, "Muvaffaqiyat", "Preview PDF saqlandi.")
        except Exception as exc:
            QMessageBox.warning(self, "Eksport xatosi", str(exc))

    def closeEvent(self, event) -> None:
        try:
            self.document.close()
        finally:
            try:
                if self.pdf_path and os.path.exists(self.pdf_path):
                    os.remove(self.pdf_path)
            except OSError:
                pass
        super().closeEvent(event)


class ReceiptPrinter:
    """A4 PDF invoice preview/print adapter used by the POS sales page."""

    PRINT_DPI = 300

    @staticmethod
    def is_printer_available() -> bool:
        try:
            return not QPrinterInfo.defaultPrinter().isNull()
        except Exception:
            return False

    @staticmethod
    def _build_customer(customer_name=None):
        """Build optional lightweight customer object for receipt rendering."""
        customer = None
        if customer_name:
            customer = SimpleNamespace(full_name=customer_name, phone=None)
        return customer

    @staticmethod
    def _build_receipt_items(cart_items):
        """Build lightweight receipt items from cart contents."""
        items = []
        total_amount = 0.0
        for item in cart_items or []:
            product = SimpleNamespace(
                name=item["product"].name,
                unit=item["product"].unit,
            )
            sale_item = SimpleNamespace(
                product=product,
                quantity=item["quantity"],
                eni=item.get("eni", item.get("width")),
                boyi=item.get("boyi", item.get("height")),
                kvm=item.get("kvm", item.get("area_sqm", item["quantity"])),
                narx_per_kvm=item.get("narx_per_kvm", item["price"]),
                width=item.get("width"),
                height=item.get("height"),
                area_sqm=item.get("area_sqm", item["quantity"]),
                price=item["price"],
            )
            items.append(sale_item)
            total_amount += float(item.get("kvm", item.get("area_sqm", item["quantity"]))) * float(
                item.get("narx_per_kvm", item["price"])
            )

        return items, total_amount

    @staticmethod
    def _build_preview_sale_object(cart_items, cashier_name, customer_name=None):
        """Build receipt-only preview data without payment or transaction fields."""
        customer = ReceiptPrinter._build_customer(customer_name)
        items, total_amount = ReceiptPrinter._build_receipt_items(cart_items)

        return SimpleNamespace(
            sale_date=datetime.now(),
            customer=customer,
            items=items,
            total_amount=total_amount,
            cashier=cashier_name or "Admin",
        )

    @staticmethod
    def _build_final_sale_object(sale, cart_items, payment_breakdown, cashier_name, customer_name=None):
        """Build final receipt data while preserving finalized sale fields."""
        customer = ReceiptPrinter._build_customer(customer_name)
        items, total_amount = ReceiptPrinter._build_receipt_items(cart_items)

        return SimpleNamespace(
            id=getattr(sale, "id", None),
            sale_date=getattr(sale, "sale_date", None) or datetime.now(),
            customer=customer,
            items=items,
            total_amount=total_amount,
            payment_breakdown=payment_breakdown or {},
            cashier=cashier_name or "Admin",
        )

    @staticmethod
    def generate_preview_receipt(cart_items, cashier_name="Admin", customer_name=None) -> str:
        """Generate preview receipt PDF without saving sale data."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_path = temp_file.name
        temp_file.close()

        preview_sale = ReceiptPrinter._build_preview_sale_object(
            cart_items=cart_items,
            cashier_name=cashier_name,
            customer_name=customer_name,
        )
        PDFGenerator.generate_preview_invoice(preview_sale, temp_path)
        return temp_path

    @staticmethod
    def generate_final_receipt(sale, cart_items, payment_breakdown, cashier_name="Admin", customer_name=None) -> str:
        """Generate final saved-sale receipt PDF with payment details."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_path = temp_file.name
        temp_file.close()

        final_sale = ReceiptPrinter._build_final_sale_object(
            sale=sale,
            cart_items=cart_items,
            payment_breakdown=payment_breakdown,
            cashier_name=cashier_name,
            customer_name=customer_name,
        )
        PDFGenerator.generate_invoice(final_sale, temp_path)
        return temp_path

    @staticmethod
    def _create_printer() -> QPrinter:
        """Create an A4 printer with crisp rasterization settings."""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.NativeFormat)
        printer.setFullPage(False)
        printer.setResolution(ReceiptPrinter.PRINT_DPI)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPageOrientation(QPageLayout.Orientation.Portrait)

        default_printer = QPrinterInfo.defaultPrinter()
        if not default_printer.isNull():
            printer.setPrinterName(default_printer.printerName())
        return printer

    @staticmethod
    def _render_pdf_to_printer(printer: QPrinter, pdf_path: str) -> None:
        """Render PDF pages to the printer at printer resolution."""
        document = QPdfDocument()
        load_status = document.load(pdf_path)
        if load_status != QPdfDocument.Error.None_:
            document.close()
            raise RuntimeError(f"PDF yuklanmadi: {load_status}")

        painter = QPainter()
        if not painter.begin(printer):
            document.close()
            raise RuntimeError("Printerga ulanib bo'lmadi")

        try:
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

            paint_rect = QRectF(printer.pageRect(QPrinter.Unit.DevicePixel))
            render_size = paint_rect.size().toSize()

            for page_index in range(document.pageCount()):
                if page_index > 0:
                    printer.newPage()

                image = document.render(page_index, render_size)
                if image.isNull():
                    raise RuntimeError("PDF sahifasi render qilinmadi")

                painter.drawImage(paint_rect, image)
        finally:
            painter.end()
            document.close()

    @staticmethod
    def print_pdf_file(pdf_path: str) -> None:
        """Print an already-generated PDF file to the default printer."""
        if not pdf_path or not os.path.exists(pdf_path):
            raise RuntimeError("PDF fayl topilmadi")
        if not ReceiptPrinter.is_printer_available():
            raise RuntimeError("Printer topilmadi")

        printer = ReceiptPrinter._create_printer()
        ReceiptPrinter._render_pdf_to_printer(printer, pdf_path)

    @staticmethod
    def preview_receipt(parent, cart_items, cashier_name="Admin", customer_name=None):
        """Preview the invoice PDF without saving a sale."""
        if not cart_items:
            return False, "Savat bo'sh"

        try:
            pdf_path = ReceiptPrinter.generate_preview_receipt(
                cart_items=cart_items,
                cashier_name=cashier_name,
                customer_name=customer_name,
            )
            dialog = PdfPreviewDialog(pdf_path, parent)
            dialog.exec()
            return True, "Chek preview ochildi"
        except Exception as exc:
            return False, f"Preview xatosi: {str(exc)}"

    @staticmethod
    def print_preview_receipt(cart_items, cashier_name="Admin", customer_name=None):
        """Print preview receipt without saving sale or including payment details."""
        if not cart_items:
            return False, "Savat bo'sh"
        if not ReceiptPrinter.is_printer_available():
            return False, "Printer topilmadi"

        pdf_path = None
        try:
            pdf_path = ReceiptPrinter.generate_preview_receipt(
                cart_items=cart_items,
                cashier_name=cashier_name,
                customer_name=customer_name,
            )
            ReceiptPrinter.print_pdf_file(pdf_path)
            return True, "Preview chek printerga yuborildi"
        except Exception as exc:
            return False, f"Printer xatosi: {str(exc)}"
        finally:
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except OSError:
                    pass

    @staticmethod
    def print_receipt(sale, cart_items, payment_breakdown, cashier_name="Admin", customer_name=None):
        """Print the invoice PDF to the default printer."""
        if not cart_items:
            return False, "Savat bo'sh"
        if not ReceiptPrinter.is_printer_available():
            return False, "Printer topilmadi"

        pdf_path = None
        try:
            pdf_path = ReceiptPrinter.generate_final_receipt(
                sale=sale,
                cart_items=cart_items,
                payment_breakdown=payment_breakdown,
                cashier_name=cashier_name,
                customer_name=customer_name,
            )
            ReceiptPrinter.print_pdf_file(pdf_path)
            return True, "Chek printerga yuborildi"
        except Exception as exc:
            return False, f"Printer xatosi: {str(exc)}"
        finally:
            if pdf_path and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except OSError:
                    pass
