# -*- coding: utf-8 -*-
"""
PDF Generator for Invoices and Reports
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

from utils.formatter import format_quantity


class PDFGenerator:
    """PDF generation for invoices and reports"""

    @staticmethod
    def generate_invoice(sale, filepath):
        """
        Generate invoice PDF (F8 preview or F12 real sale)
        Professional compact invoice layout
        """
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        left_margin = 32
        right_margin = 32
        top_margin = 38
        bottom_margin = 36
        content_width = width - left_margin - right_margin
        col_product = left_margin
        col_qty = left_margin + content_width * 0.58
        col_price = left_margin + content_width * 0.76
        col_total = left_margin + content_width * 0.90
        y = height - top_margin

        def draw_header(current_y):
            c.setFont("Helvetica-Bold", 16)
            c.drawString(left_margin, current_y, "PROFEL SAVDO")

            c.setFont("Helvetica", 10)
            c.drawString(left_margin, current_y - 18, f"Chek #{sale.id}")
            c.drawString(left_margin + 120, current_y - 18, f"Sana: {sale.sale_date.strftime('%d.%m.%Y %H:%M')}")

            next_y = current_y - 38
            if sale.customer:
                c.drawString(left_margin, next_y, f"Mijoz: {sale.customer.full_name}")
                next_y -= 15
                if sale.customer.phone:
                    c.drawString(left_margin, next_y, f"Tel: {sale.customer.phone}")
                    next_y -= 15

            c.line(left_margin, next_y, width - right_margin, next_y)
            next_y -= 18
            c.setFont("Helvetica-Bold", 10)
            c.drawString(col_product, next_y, "Mahsulot")
            c.drawRightString(col_qty + 40, next_y, "Miqdor")
            c.drawRightString(col_price + 40, next_y, "Narx")
            c.drawRightString(width - right_margin, next_y, "Jami")
            next_y -= 6
            c.line(left_margin, next_y, width - right_margin, next_y)
            return next_y - 16

        y = draw_header(y)
        c.setFont("Helvetica", 9)
        for item in sale.items:
            if y < bottom_margin + 110:
                c.showPage()
                y = height - top_margin
                y = draw_header(y)
                c.setFont("Helvetica", 9)

            product_name = item.product.name
            if len(product_name) > 52:
                product_name = product_name[:49] + "..."

            c.drawString(col_product, y, product_name)
            c.drawRightString(col_qty + 40, y, format_quantity(item.quantity, item.product.unit))
            c.drawRightString(col_price + 40, y, f"{item.price:,.0f}")
            c.drawRightString(width - right_margin, y, f"{item.quantity * item.price:,.0f}")
            y -= 16

        c.line(left_margin, y, width - right_margin, y)
        y -= 22

        c.setFont("Helvetica-Bold", 12)
        c.drawString(col_price - 10, y, "JAMI:")
        c.drawRightString(width - right_margin, y, f"{sale.total_amount:,.0f} so'm")

        if sale.payment_breakdown:
            y -= 24
            c.setFont("Helvetica", 10)
            c.drawString(left_margin, y, "To'lov:")

            if sale.payment_breakdown.get('naqd', 0) > 0:
                y -= 15
                c.drawString(left_margin + 18, y, f"Naqd: {sale.payment_breakdown['naqd']:,.0f} so'm")

            if sale.payment_breakdown.get('karta', 0) > 0:
                y -= 15
                c.drawString(left_margin + 18, y, f"Karta: {sale.payment_breakdown['karta']:,.0f} so'm")

            if sale.payment_breakdown.get('click', 0) > 0:
                y -= 15
                c.drawString(left_margin + 18, y, f"Click: {sale.payment_breakdown['click']:,.0f} so'm")

            if sale.payment_breakdown.get('qarz', 0) > 0:
                y -= 15
                c.drawString(left_margin + 18, y, f"Qarz: {sale.payment_breakdown['qarz']:,.0f} so'm")

        c.setFont("Helvetica", 8)
        c.drawString(left_margin, 42, "Rahmat! Yana kuting!")
        c.drawString(left_margin, 28, f"Kassir: {sale.cashier}")

        c.save()

    @staticmethod
    def generate_report(sales, filepath, start_date, end_date):
        """
        Generate multi-sale report PDF
        Compact accounting style, A4 optimized
        """
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        # Header
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 50, "SAVDO HISOBOTI")

        c.setFont("Helvetica", 10)
        date_range = f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
        c.drawString(50, height - 70, f"Davr: {date_range}")

        # Summary
        total_sales = len(sales)
        total_revenue = sum(s.total_amount for s in sales)
        total_profit = sum(s.profit for s in sales)

        c.drawString(50, height - 90, f"Savdolar soni: {total_sales}")
        c.drawString(200, height - 90, f"Daromad: {total_revenue:,.0f} so'm")
        c.drawString(400, height - 90, f"Foyda: {total_profit:,.0f} so'm")

        # Line
        c.line(50, height - 100, width - 50, height - 100)

        # Table
        y_offset = 120
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, height - y_offset, "Sana")
        c.drawString(130, height - y_offset, "Mijoz")
        c.drawString(250, height - y_offset, "To'lov")
        c.drawString(350, height - y_offset, "Summa")
        c.drawString(450, height - y_offset, "Foyda")

        y_offset += 5
        c.line(50, height - y_offset, width - 50, height - y_offset)

        c.setFont("Helvetica", 8)
        y_offset += 15

        for sale in sales:
            if y_offset > height - 80:
                c.showPage()
                y_offset = 50

            date_str = sale.sale_date.strftime("%d.%m %H:%M")
            customer_name = sale.customer.full_name[:15] if sale.customer else "-"
            payment_type = sale.payment_type[:10]

            c.drawString(50, height - y_offset, date_str)
            c.drawString(130, height - y_offset, customer_name)
            c.drawString(250, height - y_offset, payment_type)
            c.drawString(350, height - y_offset, f"{sale.total_amount:,.0f}")
            c.drawString(450, height - y_offset, f"{sale.profit:,.0f}")

            y_offset += 12

        # Footer
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Yaratildi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

        c.save()
