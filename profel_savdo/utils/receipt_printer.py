# -*- coding: utf-8 -*-
"""
Receipt printing — to'g'ridan-to'g'ri A4 PDF → printer.

F8 yoki F12 bosilganda preview oynasi ochilmaydi,
chek avtomatik printerga yuboriladi.
Printer mavjud bo'lmasa foydalanuvchiga aniq xabar beriladi.
"""
from __future__ import annotations

import os
import tempfile
from datetime import datetime
from types import SimpleNamespace

from PySide6.QtCore import QMarginsF, QRectF
from PySide6.QtGui import QPainter, QPageLayout, QPageSize
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPrintSupport import QPrinter, QPrinterInfo

from reports.pdf_generator import PDFGenerator


class ReceiptPrinter:
    """A4 PDF → printer adapter. Preview oynasisiz, to'g'ridan-to'g'ri chop etadi."""

    PRINT_DPI = 300

    # ──────────────────────────────────────────────────────────────────────
    #  Printer mavjudligini tekshirish
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def is_printer_available() -> bool:
        try:
            return not QPrinterInfo.defaultPrinter().isNull()
        except Exception:
            return False

    @staticmethod
    def get_printer_name() -> str:
        """Default printer nomini qaytaradi, yo'q bo'lsa bo'sh satr."""
        try:
            info = QPrinterInfo.defaultPrinter()
            return info.printerName() if not info.isNull() else ""
        except Exception:
            return ""

    # ──────────────────────────────────────────────────────────────────────
    #  Sale ob'ektlarini qurish
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _build_customer(customer_name=None):
        if customer_name:
            return SimpleNamespace(full_name=customer_name, phone=None)
        return None

    @staticmethod
    def _build_receipt_items(cart_items):
        items = []
        total_amount = 0.0
        for item in cart_items or []:
            product = SimpleNamespace(
                name=item["product"].name,
                unit=getattr(item["product"], "unit", "kvm"),
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
            total_amount += float(
                item.get("kvm", item.get("area_sqm", item["quantity"]))
            ) * float(item.get("narx_per_kvm", item["price"]))
        return items, total_amount

    @staticmethod
    def _build_preview_sale_object(cart_items, cashier_name, customer_name=None):
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
    def _build_final_sale_object(
        sale, cart_items, payment_breakdown, cashier_name, customer_name=None
    ):
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

    # ──────────────────────────────────────────────────────────────────────
    #  PDF generatsiya
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def generate_preview_receipt(
        cart_items, cashier_name="Admin", customer_name=None
    ) -> str:
        """F8 — ro'yxat cheki PDF yaratadi (to'lovsiz)."""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        path = tmp.name
        tmp.close()
        sale_obj = ReceiptPrinter._build_preview_sale_object(
            cart_items, cashier_name, customer_name
        )
        PDFGenerator.generate_preview_invoice(sale_obj, path)
        return path

    @staticmethod
    def generate_final_receipt(
        sale, cart_items, payment_breakdown, cashier_name="Admin", customer_name=None
    ) -> str:
        """F12 — final chek PDF yaratadi (to'lov bilan)."""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        path = tmp.name
        tmp.close()
        sale_obj = ReceiptPrinter._build_final_sale_object(
            sale, cart_items, payment_breakdown, cashier_name, customer_name
        )
        PDFGenerator.generate_invoice(sale_obj, path)
        return path

    # ──────────────────────────────────────────────────────────────────────
    #  Printer sozlamalari
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def _create_printer() -> QPrinter:
        """A4, fixed size, zero margins — printer format o'zgartirmasin."""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.NativeFormat)
        printer.setResolution(ReceiptPrinter.PRINT_DPI)

        page_size = QPageSize(QPageSize.PageSizeId.A4)
        layout = QPageLayout(
            page_size,
            QPageLayout.Orientation.Portrait,
            QMarginsF(0, 0, 0, 0),
        )
        printer.setPageLayout(layout)
        printer.setFullPage(True)

        info = QPrinterInfo.defaultPrinter()
        if not info.isNull():
            printer.setPrinterName(info.printerName())
        return printer

    @staticmethod
    def _render_pdf_to_printer(printer: QPrinter, pdf_path: str) -> None:
        """PDF sahifalarini printer DPI da rasterlab chop etadi."""
        document = QPdfDocument()
        if document.load(pdf_path) != QPdfDocument.Error.None_:
            document.close()
            raise RuntimeError("PDF fayl o'qilmadi")

        painter = QPainter()
        if not painter.begin(printer):
            document.close()
            raise RuntimeError("Printerga ulanib bo'lmadi")

        try:
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

            rect = QRectF(printer.pageRect(QPrinter.Unit.DevicePixel))
            size = rect.size().toSize()

            for i in range(document.pageCount()):
                if i > 0:
                    printer.newPage()
                img = document.render(i, size)
                if img.isNull():
                    raise RuntimeError(f"{i+1}-sahifa render qilinmadi")
                painter.drawImage(rect, img)
        finally:
            painter.end()
            document.close()

    # ──────────────────────────────────────────────────────────────────────
    #  Asosiy print metodi
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def print_pdf_file(pdf_path: str) -> None:
        """Tayyor PDF faylni printerga yuboradi."""
        if not pdf_path or not os.path.exists(pdf_path):
            raise RuntimeError("PDF fayl topilmadi")
        if not ReceiptPrinter.is_printer_available():
            printer_msg = (
                "Printer topilmadi!\n\n"
                "Iltimos:\n"
                "  • Printer ulanganligini tekshiring\n"
                "  • Windows → Qurilmalar → Printerlar bo'limida\n"
                "    default printer o'rnatilganligini tekshiring"
            )
            raise RuntimeError(printer_msg)
        printer = ReceiptPrinter._create_printer()
        ReceiptPrinter._render_pdf_to_printer(printer, pdf_path)

    # ──────────────────────────────────────────────────────────────────────
    #  F8 — Ro'yxat cheki (to'lovsiz, to'g'ridan-to'g'ri printer)
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def print_preview_receipt(
        cart_items, cashier_name="Admin", customer_name=None
    ) -> tuple[bool, str]:
        """
        F8 bosilganda chaqiriladi.
        Preview oynasi ochilmaydi — to'g'ridan-to'g'ri printerga yuboriladi.
        """
        if not cart_items:
            return False, "Savat bo'sh"

        if not ReceiptPrinter.is_printer_available():
            return False, (
                "Printer topilmadi!\n\n"
                "Iltimos printerning ulangan va\n"
                "standart printer sifatida o'rnatilganligini tekshiring."
            )

        pdf_path = None
        try:
            pdf_path = ReceiptPrinter.generate_preview_receipt(
                cart_items, cashier_name, customer_name
            )
            ReceiptPrinter.print_pdf_file(pdf_path)
            printer_name = ReceiptPrinter.get_printer_name()
            msg = f"Ro'yxat cheki printerga yuborildi."
            if printer_name:
                msg += f"\nPrinter: {printer_name}"
            return True, msg
        except Exception as exc:
            return False, f"Chop etish xatosi:\n{str(exc)}"
        finally:
            _safe_remove(pdf_path)

    # ──────────────────────────────────────────────────────────────────────
    #  F12 — Final chek (to'lov bilan, to'g'ridan-to'g'ri printer)
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def print_receipt(
        sale, cart_items, payment_breakdown,
        cashier_name="Admin", customer_name=None
    ) -> tuple[bool, str]:
        """
        F12 savdo yakunlanganda chaqiriladi.
        Preview oynasi ochilmaydi — to'g'ridan-to'g'ri printerga yuboriladi.
        """
        if not cart_items:
            return False, "Savat bo'sh"

        if not ReceiptPrinter.is_printer_available():
            return False, (
                "Printer topilmadi!\n\n"
                "Savdo saqlandi, lekin chek chop etilmadi.\n"
                "Iltimos printerning ulangan va\n"
                "standart printer sifatida o'rnatilganligini tekshiring."
            )

        pdf_path = None
        try:
            pdf_path = ReceiptPrinter.generate_final_receipt(
                sale, cart_items, payment_breakdown, cashier_name, customer_name
            )
            ReceiptPrinter.print_pdf_file(pdf_path)
            printer_name = ReceiptPrinter.get_printer_name()
            msg = f"Chek printerga yuborildi."
            if printer_name:
                msg += f"\nPrinter: {printer_name}"
            return True, msg
        except Exception as exc:
            return False, f"Chop etish xatosi:\n{str(exc)}"
        finally:
            _safe_remove(pdf_path)

    # ──────────────────────────────────────────────────────────────────────
    #  Qolgan metodlar (backward compatibility)
    # ──────────────────────────────────────────────────────────────────────

    @staticmethod
    def preview_receipt(parent, cart_items, cashier_name="Admin", customer_name=None):
        """
        Eski preview metodi — endi ham to'g'ridan-to'g'ri printer.
        (PdfPreviewDialog olib tashlandi)
        """
        return ReceiptPrinter.print_preview_receipt(
            cart_items, cashier_name, customer_name
        )


# ──────────────────────────────────────────────────────────────────────────
#  Yordamchi
# ──────────────────────────────────────────────────────────────────────────

def _safe_remove(path: str | None) -> None:
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass
