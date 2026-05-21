# -*- coding: utf-8 -*-
"""
PDF Generator for Invoices and Reports
A4 format – har bir oyna turi uchun alohida jadval,
oyna summasi, grand total, to'lov breakdown.
"""
from collections import defaultdict, OrderedDict
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from config.constants import APP_NAME
from utils.formatter import format_square_meters, format_decimal

# ── Ranglar ────────────────────────────────────────────────────────────────
C_DARK   = colors.HexColor("#102331")   # sarlavha fon
C_HEAD   = colors.HexColor("#1a3a52")   # jadval header fon
C_ROW_A  = colors.HexColor("#f0f8fb")   # alternating row 1
C_ROW_B  = colors.white                  # alternating row 2
C_TOTAL  = colors.HexColor("#dbeafe")   # oyna jami qatori
C_GRAND  = colors.HexColor("#102331")   # grand total fon
C_BORDER = colors.HexColor("#94c8d8")   # chiziq rangi
C_ACCENT = colors.HexColor("#2563eb")   # to'lov rangi

# ── O'lchamlar ────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4            # 595.28 x 841.89 pt
L_MARGIN = 18 * mm
R_MARGIN = 18 * mm
T_MARGIN = 20 * mm
B_MARGIN = 22 * mm
CONTENT_W = PAGE_W - L_MARGIN - R_MARGIN


# ══════════════════════════════════════════════════════════════════════════
#  Yordamchi funksiyalar
# ══════════════════════════════════════════════════════════════════════════

def _fmt_num(value):
    """Sonni 3 xonali ajratib formatlash (masalan 13 449 500)."""
    try:
        return f"{float(value):,.4f}".rstrip('0').rstrip('.')
    except Exception:
        return str(value)


def _fmt_sum(value):
    """Summani butun son sifatida formatlash."""
    try:
        return f"{float(value):,.0f}"
    except Exception:
        return str(value)


def _group_items_by_product(items):
    """cart items / sale.items ni mahsulot nomiga ko'ra guruhlash."""
    groups = OrderedDict()
    for item in items:
        name = item.product.name
        if name not in groups:
            groups[name] = []
        groups[name].append(item)
    return groups


# ══════════════════════════════════════════════════════════════════════════
#  Canvas yordamchi metodlari
# ══════════════════════════════════════════════════════════════════════════

class _Doc:
    """Yengilroq canvas wrapper: sahifa, y-tracker, header/footer."""

    def __init__(self, filepath, is_preview=False):
        self.c = canvas.Canvas(filepath, pagesize=A4)
        self.is_preview = is_preview
        self.page_num = 1
        self.y = PAGE_H - T_MARGIN

    # ── Sahifa operatsiyalari ──────────────────────────────────────────────

    def new_page(self):
        self.c.showPage()
        self.page_num += 1
        self.y = PAGE_H - T_MARGIN

    def ensure_space(self, needed):
        """needed pt bo'sh joy kerak bo'lsa yangi sahifa ochadi."""
        if self.y < B_MARGIN + needed:
            self.new_page()

    # ── Chiziqlar ─────────────────────────────────────────────────────────

    def hline(self, y=None, color=C_BORDER, width=0.5):
        y = y if y is not None else self.y
        self.c.setStrokeColor(color)
        self.c.setLineWidth(width)
        self.c.line(L_MARGIN, y, PAGE_W - R_MARGIN, y)

    # ── Matn ──────────────────────────────────────────────────────────────

    def text(self, x, y, txt, font="Helvetica", size=9, color=colors.black):
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        self.c.drawString(x, y, txt)

    def rtext(self, x, y, txt, font="Helvetica", size=9, color=colors.black):
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        self.c.drawRightString(x, y, txt)

    def ctext(self, x, y, w, txt, font="Helvetica", size=9, color=colors.black):
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        self.c.drawCentredString(x + w / 2, y, txt)

    # ── To'ldirilgan to'rtburchak ──────────────────────────────────────────

    def filled_rect(self, x, y, w, h, fill, stroke=None, line_w=0.3):
        self.c.setFillColor(fill)
        if stroke:
            self.c.setStrokeColor(stroke)
            self.c.setLineWidth(line_w)
            self.c.rect(x, y, w, h, fill=1, stroke=1)
        else:
            self.c.rect(x, y, w, h, fill=1, stroke=0)

    def save(self):
        self.c.save()


# ══════════════════════════════════════════════════════════════════════════
#  Katta sarlavha bloki
# ══════════════════════════════════════════════════════════════════════════

def _draw_header(doc, sale, is_preview=False):
    """
    Sahifa tepasiga chiroyli sarlavha chizadi.
    Qaytariladi: sarlavhadan keyin qolgan y pozitsiyasi.
    """
    c = doc.c
    x0 = L_MARGIN
    y0 = doc.y

    # ── Fon paneli ───────────────────────────────────────────────────────
    panel_h = 52 if not (hasattr(sale, 'customer') and sale.customer) else 62
    doc.filled_rect(x0, y0 - panel_h, CONTENT_W, panel_h, C_DARK)

    # Kompaniya nomi
    doc.text(x0 + 8, y0 - 16, APP_NAME, "Helvetica-Bold", 15, colors.white)

    # Tur belgisi (chek / ro'yxat)
    if is_preview:
        badge_txt = "RO'YXAT CHEKI"
        badge_color = colors.HexColor("#f59e0b")
    else:
        badge_txt = "HISOB-CHEK"
        badge_color = colors.HexColor("#22c55e")

    bw = 72
    doc.filled_rect(PAGE_W - R_MARGIN - bw - 8, y0 - 20, bw, 14,
                    badge_color)
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(colors.white)
    c.drawCentredString(PAGE_W - R_MARGIN - bw / 2 - 8, y0 - 9, badge_txt)

    # Sana & chek raqami
    sana = sale.sale_date.strftime("%d.%m.%Y  %H:%M")
    sale_id = getattr(sale, 'id', None)
    if sale_id:
        id_txt = f"Chek: #{sale_id}   |   Sana: {sana}"
    else:
        id_txt = f"Sana: {sana}"
    doc.text(x0 + 8, y0 - 32, id_txt, "Helvetica", 8.5, colors.HexColor("#a0ccd8"))

    # Kassir
    cashier = getattr(sale, 'cashier', 'Admin') or 'Admin'
    doc.text(x0 + 8, y0 - 44, f"Kassir: {cashier}", "Helvetica", 8.5,
             colors.HexColor("#a0ccd8"))

    # Mijoz (agar mavjud)
    cy = y0 - panel_h + 10
    if hasattr(sale, 'customer') and sale.customer:
        doc.text(x0 + 8, cy,
                 f"Mijoz: {sale.customer.full_name}",
                 "Helvetica-Bold", 9, colors.HexColor("#7dd3fc"))

    doc.y = y0 - panel_h - 6
    return doc.y


# ══════════════════════════════════════════════════════════════════════════
#  Bitta oyna jadvali
# ══════════════════════════════════════════════════════════════════════════

# Ustun kengliklari nisbati (jami = CONTENT_W)
_COL_RATIOS = [0.05, 0.28, 0.13, 0.13, 0.10, 0.16, 0.15]
_COL_HEADERS = ["№", "Oyna", "Eni", "Bo'yi", "Dona", "Maydon (m²)", "Summa"]


def _col_widths():
    return [CONTENT_W * r for r in _COL_RATIOS]


def _row_height():
    return 16  # pt


def _draw_window_table(doc, window_name, rows, start_num=1):
    """
    Bitta oyna turi uchun jadval chizadi.
    rows: list of (eni, boyi, qty, kvm, narx_per_kvm)
    start_num: qator raqami boshlash (global)
    Qaytaradi: jadval oxirida y pozitsiyasi va so'nggi qator raqami.
    """
    CW = _col_widths()
    RH = _row_height()
    x0 = L_MARGIN

    # ── Oyna sarlavhasi ───────────────────────────────────────────────────
    title_h = 18
    doc.ensure_space(title_h + RH * 3 + 30)  # kamida 3 qator + jami

    # Sarlavha fon
    doc.filled_rect(x0, doc.y - title_h, CONTENT_W, title_h,
                    colors.HexColor("#1e4a6b"), C_BORDER, 0.4)
    doc.text(x0 + 6, doc.y - 12, window_name,
             "Helvetica-Bold", 9.5, colors.HexColor("#e0f2fe"))
    doc.y -= title_h

    # ── Jadval sarlavhasi ─────────────────────────────────────────────────
    doc.filled_rect(x0, doc.y - RH, CONTENT_W, RH,
                    C_HEAD, C_BORDER, 0.4)
    cx = x0
    for i, (hdr, cw) in enumerate(zip(_COL_HEADERS, CW)):
        align = "right" if i >= 2 else "left"
        pad = 4
        if align == "right":
            doc.rtext(cx + cw - pad, doc.y - RH + 4, hdr,
                      "Helvetica-Bold", 7.5, colors.white)
        else:
            doc.text(cx + pad, doc.y - RH + 4, hdr,
                     "Helvetica-Bold", 7.5, colors.white)
        cx += cw
    doc.y -= RH

    # ── Qatorlar ─────────────────────────────────────────────────────────
    window_total_kvm = 0.0
    window_total_sum = 0.0
    num = start_num

    for idx, (eni, boyi, qty, kvm, narx_per_kvm) in enumerate(rows):
        # Yangi sahifaga o'tish kerakmi?
        doc.ensure_space(RH + 24)  # 1 qator + jami xonasi

        row_color = C_ROW_A if idx % 2 == 0 else C_ROW_B
        doc.filled_rect(x0, doc.y - RH, CONTENT_W, RH,
                        row_color, C_BORDER, 0.3)

        line_sum = kvm * narx_per_kvm
        window_total_kvm += kvm
        window_total_sum += line_sum

        values = [
            str(num),
            "",          # Steklo — sarlavhada ko'rinadi
            _fmt_num(eni),
            _fmt_num(boyi),
            str(int(qty)) if float(qty) == int(float(qty)) else _fmt_num(qty),
            _fmt_num(kvm),
            _fmt_sum(line_sum),
        ]

        cx = x0
        for i, (val, cw) in enumerate(zip(values, CW)):
            pad = 4
            txt_color = C_DARK
            if i == 0:  # №
                doc.ctext(cx, doc.y - RH + 4, cw, val,
                          "Helvetica", 8, txt_color)
            elif i == 1:  # Steklo — bo'sh (sarlavhada)
                pass
            elif i >= 2:  # raqamlar o'ngga
                doc.rtext(cx + cw - pad, doc.y - RH + 4, val,
                          "Helvetica", 8, txt_color)
            cx += cw

        doc.y -= RH
        num += 1

    # ── Oyna jami qatori ─────────────────────────────────────────────────
    doc.ensure_space(RH + 4)
    doc.filled_rect(x0, doc.y - RH, CONTENT_W, RH,
                    C_TOTAL, C_BORDER, 0.5)

    # "Jami" matni
    doc.text(x0 + 6, doc.y - RH + 4,
             f"Jami ({window_name}):",
             "Helvetica-Bold", 8.5, C_DARK)

    # KVM jami
    kvm_x = x0 + sum(CW[:5])
    doc.rtext(kvm_x + CW[5] - 4, doc.y - RH + 4,
              _fmt_num(window_total_kvm),
              "Helvetica-Bold", 8.5, C_DARK)

    # Summa jami
    doc.rtext(x0 + CONTENT_W - 4, doc.y - RH + 4,
              _fmt_sum(window_total_sum),
              "Helvetica-Bold", 8.5, colors.HexColor("#1d4ed8"))

    doc.y -= RH + 5  # qatordan keyin biroz bo'shliq

    return doc.y, num, window_total_kvm, window_total_sum


# ══════════════════════════════════════════════════════════════════════════
#  Grand Total bloki
# ══════════════════════════════════════════════════════════════════════════

def _draw_grand_total(doc, grand_kvm, grand_sum,
                      payment_breakdown=None, is_preview=False):
    """Hamma oynalar jami + to'lov blokini chizadi."""
    doc.ensure_space(70)
    x0 = L_MARGIN
    c = doc.c

    # ── Separator ────────────────────────────────────────────────────────
    doc.hline(doc.y, C_DARK, 1.0)
    doc.y -= 3

    # ── Grand total paneli ────────────────────────────────────────────────
    gt_h = 26
    doc.filled_rect(x0, doc.y - gt_h, CONTENT_W, gt_h, C_GRAND)

    # Chap: "UMUMIY SUMMA" matni
    doc.text(x0 + 8, doc.y - gt_h + 10,
             f"UMUMIY SUMMA  (KVM: {_fmt_num(grand_kvm)})",
             "Helvetica-Bold", 10, colors.white)

    # O'ng: summa
    doc.rtext(x0 + CONTENT_W - 8, doc.y - gt_h + 10,
              f"{_fmt_sum(grand_sum)} so'm",
              "Helvetica-Bold", 13, colors.HexColor("#86efac"))

    doc.y -= gt_h + 6

    # ── To'lov bo'limi (faqat final chekda) ──────────────────────────────
    if payment_breakdown and not is_preview:
        pay_labels = {
            'naqd':  ("Naqd pul",   colors.HexColor("#16a34a")),
            'karta': ("Karta",      colors.HexColor("#2563eb")),
            'click': ("Click/UZUM", colors.HexColor("#7c3aed")),
            'qarz':  ("Qarz",       colors.HexColor("#dc2626")),
        }
        active = {k: v for k, v in payment_breakdown.items() if float(v or 0) > 0}
        if active:
            doc.ensure_space(12 + len(active) * 18 + 8)
            # Sarlavha
            doc.text(x0, doc.y - 11, "To'lov ma'lumotlari:",
                     "Helvetica-Bold", 9, C_DARK)
            doc.y -= 14

            pay_w = CONTENT_W / 2
            for key, amount in active.items():
                label, lcolor = pay_labels.get(key, (key.capitalize(), C_ACCENT))
                doc.filled_rect(x0, doc.y - 14, pay_w, 14,
                                colors.HexColor("#f0f9ff"))
                doc.text(x0 + 6, doc.y - 10, label,
                         "Helvetica-Bold", 9, lcolor)
                doc.rtext(x0 + pay_w - 6, doc.y - 10,
                          f"{_fmt_sum(amount)} so'm",
                          "Helvetica-Bold", 9, lcolor)
                doc.y -= 15

            doc.y -= 4

    elif is_preview:
        # Preview uchun eslatma
        doc.ensure_space(18)
        doc.filled_rect(x0, doc.y - 16, CONTENT_W, 16,
                        colors.HexColor("#fef9c3"))
        doc.text(x0 + 6, doc.y - 10,
                 "ESLATMA: Bu ro'yxat cheki. To'lov qilinmagan va ombor rezerv qilinmagan.",
                 "Helvetica-Oblique", 7.5, colors.HexColor("#92400e"))
        doc.y -= 18


# ══════════════════════════════════════════════════════════════════════════
#  Footer
# ══════════════════════════════════════════════════════════════════════════

def _draw_footer(doc, note=None):
    """Sahifa pastida footer."""
    c = doc.c
    y_foot = B_MARGIN - 4
    doc.hline(y_foot + 10, C_BORDER, 0.5)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(L_MARGIN, y_foot,
                 f"Yaratildi: {datetime.now().strftime('%d.%m.%Y %H:%M')}   |   {APP_NAME}")
    if note:
        c.drawRightString(PAGE_W - R_MARGIN, y_foot, f"Izoh: {note}")


# ══════════════════════════════════════════════════════════════════════════
#  Sale items → rows converter
# ══════════════════════════════════════════════════════════════════════════

def _item_to_row(item):
    """sale.item yoki cart_item dan (eni, boyi, qty, kvm, narx) oladi."""
    # is not None tekshiruvi — 0.0 falsy bo'lishi uchun
    eni_val  = item.eni  if item.eni  is not None else item.width
    boyi_val = item.boyi if item.boyi is not None else item.height
    kvm_val  = item.kvm  if item.kvm  is not None else item.area_sqm
    if kvm_val is None:
        kvm_val = item.quantity

    eni  = float(eni_val  or 0)
    boyi = float(boyi_val or 0)
    kvm  = float(kvm_val  or 0)
    narx = float(item.narx_per_kvm if item.narx_per_kvm is not None else item.price or 0)

    if eni > 0 and boyi > 0:
        one_kvm = eni * boyi
        qty = round(kvm / one_kvm) if one_kvm > 0 else 1
    else:
        qty = 1
    return (eni, boyi, qty, kvm, narx)


# ══════════════════════════════════════════════════════════════════════════
#  Asosiy generator
# ══════════════════════════════════════════════════════════════════════════

def _build_invoice(sale, filepath, is_preview=False):
    """
    Umumiy invoice qurilishi.
    is_preview=True  → F8 ro'yxat chek (to'lov ko'rsatilmaydi)
    is_preview=False → final chek (to'lov breakdown ko'rsatiladi)
    """
    doc = _Doc(filepath, is_preview=is_preview)

    # ── Sarlavha ──────────────────────────────────────────────────────────
    _draw_header(doc, sale, is_preview=is_preview)
    doc.y -= 8

    # ── Mahsulotlarni guruhlash ───────────────────────────────────────────
    groups = _group_items_by_product(sale.items)

    grand_kvm = 0.0
    grand_sum = 0.0
    row_num = 1

    for window_name, items in groups.items():
        rows = [_item_to_row(it) for it in items]
        doc.y, row_num, w_kvm, w_sum = _draw_window_table(
            doc, window_name, rows, start_num=row_num
        )
        grand_kvm += w_kvm
        grand_sum += w_sum
        doc.y -= 4  # jadvallar orasida bo'shliq

    # ── Grand total ───────────────────────────────────────────────────────
    payment_breakdown = getattr(sale, 'payment_breakdown', None)
    _draw_grand_total(doc, grand_kvm, grand_sum,
                      payment_breakdown=payment_breakdown,
                      is_preview=is_preview)

    # ── Izoh (note) ───────────────────────────────────────────────────────
    note = getattr(sale, 'note', None)
    _draw_footer(doc, note=note)

    doc.save()


# ══════════════════════════════════════════════════════════════════════════
#  PUBLIC API (o'zgarishsiz — receipt_printer.py bilan muvofiqlashtirilgan)
# ══════════════════════════════════════════════════════════════════════════

class PDFGenerator:
    """PDF generation for invoices and reports."""

    @staticmethod
    def generate_invoice(sale, filepath):
        """Final savdo cheki — to'lov breakdown bilan."""
        _build_invoice(sale, filepath, is_preview=False)

    @staticmethod
    def generate_preview_invoice(preview_sale, filepath):
        """F8 ro'yxat cheki — to'lov ko'rsatilmaydi."""
        _build_invoice(preview_sale, filepath, is_preview=True)

    @staticmethod
    def generate_report(sales, filepath, start_date, end_date):
        """
        Ko'p savdoli hisobot PDF (o'zgarmadi).
        """
        from utils.formatter import format_square_meters as fsm
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 50, f"{APP_NAME} HISOBOTI")

        c.setFont("Helvetica", 10)
        date_range = (f"{start_date.strftime('%d.%m.%Y')} - "
                      f"{end_date.strftime('%d.%m.%Y')}")
        c.drawString(50, height - 70, f"Davr: {date_range}")

        total_sales = len(sales)
        total_revenue = sum(s.total_amount for s in sales)
        total_profit = sum(s.profit for s in sales)
        total_kvm = 0
        top_glass_totals = {}
        for sale in sales:
            for item in sale.items:
                if not item.product:
                    continue
                item_kvm = item.kvm or item.area_sqm or item.quantity or 0
                total_kvm += item_kvm
                top_glass_totals[item.product.name] = (
                    top_glass_totals.get(item.product.name, 0) + item_kvm
                )

        top_glass = "-"
        if top_glass_totals:
            glass_name, glass_kvm = max(
                top_glass_totals.items(), key=lambda x: x[1]
            )
            top_glass = f"{glass_name} ({fsm(glass_kvm)})"

        c.drawString(50, height - 90,
                     f"Savdolar soni: {total_sales}")
        c.drawString(200, height - 90,
                     f"Daromad: {total_revenue:,.0f} so'm")
        c.drawString(400, height - 90,
                     f"Foyda: {total_profit:,.0f} so'm")
        c.drawString(50, height - 108,
                     f"Sotilgan KVM: {fsm(total_kvm)}")
        c.drawString(250, height - 108,
                     f"Eng ko'p sotilgan oyna: {top_glass[:38]}")

        c.line(50, height - 118, width - 50, height - 118)

        y_offset = 138
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50,  height - y_offset, "Sana")
        c.drawString(130, height - y_offset, "Mijoz")
        c.drawString(240, height - y_offset, "Oyna")
        c.drawString(360, height - y_offset, "KVM")
        c.drawString(420, height - y_offset, "Summa")
        c.drawString(500, height - y_offset, "Foyda")

        y_offset += 5
        c.line(50, height - y_offset, width - 50, height - y_offset)

        c.setFont("Helvetica", 8)
        y_offset += 15

        for sale in sales:
            if y_offset > height - 80:
                c.showPage()
                y_offset = 50

            date_str = sale.sale_date.strftime("%d.%m %H:%M")
            customer_name = (
                sale.customer.full_name[:15] if sale.customer else "-"
            )
            product_names = ", ".join(
                item.product.name
                for item in sale.items
                if getattr(item, "product", None)
            )[:20] or "-"
            sale_kvm = sum(
                item.kvm or item.area_sqm or item.quantity or 0
                for item in sale.items
            )

            c.drawString(50,  height - y_offset, date_str)
            c.drawString(130, height - y_offset, customer_name)
            c.drawString(240, height - y_offset, product_names)
            c.drawString(360, height - y_offset, fsm(sale_kvm))
            c.drawString(420, height - y_offset, f"{sale.total_amount:,.0f}")
            c.drawString(500, height - y_offset, f"{sale.profit:,.0f}")

            y_offset += 12

        c.setFont("Helvetica", 8)
        c.drawString(50, 30,
                     f"Yaratildi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        c.save()
