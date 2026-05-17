# -*- coding: utf-8 -*-
"""
Design System - Modern Warehouse POS Style
"""
from config.constants import COLORS, FONT_FAMILY, FONT_SIZE_NORMAL


def get_stylesheet():
    """Get main application stylesheet"""
    return f"""
    /* ========================================
       GLOBAL STYLES
       ======================================== */

    QWidget {{
        font-family: "{FONT_FAMILY}";
        font-size: {FONT_SIZE_NORMAL}px;
        color: {COLORS['text_dark']};
    }}

    QMainWindow {{
        background-color: {COLORS['bg_main']};
    }}

    /* ========================================
       TOP BAR
       ======================================== */

    QFrame#topBar {{
        background-color: {COLORS['dark_panel']};
        border-bottom: 2px solid {COLORS['primary']};
    }}

    QLabel#appTitle {{
        color: {COLORS['text_light']};
        font-size: 18px;
        font-weight: 600;
    }}

    QLabel#clockLabel {{
        color: {COLORS['primary']};
        font-size: 14px;
        font-weight: 500;
    }}

    QLabel#userLabel {{
        color: {COLORS['text_muted']};
        font-size: 12px;
    }}

    /* ========================================
       SIDEBAR
       ======================================== */

    QFrame#sidebar {{
        background-color: {COLORS['dark_panel']};
        border-right: 1px solid {COLORS['dark_panel_alt']};
    }}

    QPushButton#menuButton {{
        background-color: transparent;
        color: {COLORS['text_light']};
        border: none;
        border-radius: 6px;
        padding: 10px 16px;
        text-align: left;
        font-size: 13px;
        font-weight: 500;
    }}

    QPushButton#menuButton:hover {{
        background-color: {COLORS['dark_panel_alt']};
    }}

    QPushButton#menuButton[active="true"] {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_dark']};
        font-weight: 600;
    }}

    /* ========================================
       BUTTONS
       ======================================== */

    QPushButton {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_dark']};
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
    }}

    QPushButton:hover {{
        background-color: {COLORS['primary_dark']};
    }}

    QPushButton:pressed {{
        background-color: {COLORS['dark_panel_alt']};
    }}

    QPushButton:disabled {{
        background-color: {COLORS['text_muted']};
        color: #999;
    }}

    QPushButton#btnSuccess {{
        background-color: {COLORS['success']};
        color: white;
    }}

    QPushButton#btnSuccess:hover {{
        background-color: #229954;
    }}

    QPushButton#btnWarning {{
        background-color: {COLORS['warning']};
        color: white;
    }}

    QPushButton#btnWarning:hover {{
        background-color: #e67e22;
    }}

    QPushButton#btnDanger {{
        background-color: {COLORS['danger']};
        color: white;
    }}

    QPushButton#btnDanger:hover {{
        background-color: #c0392b;
    }}

    /* ========================================
       TABLES
       ======================================== */

    QTableWidget {{
        background-color: #F8FAFC;
        alternate-background-color: #F1F5F9;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        gridline-color: #CBD5E1;
        selection-background-color: #38bdf8;
        selection-color: #ffffff;
        color: #0F172A;
    }}

    QTableWidget::item {{
        padding: 8px;
        color: #0F172A;
        border: none;
    }}

    QTableWidget::item:hover {{
        background-color: #E0F2FE;
        color: #0F172A;
    }}

    QTableWidget::item:selected {{
        background-color: #38bdf8;
        color: #ffffff;
    }}

    QTableWidget::item:selected:hover {{
        background-color: #38bdf8;
        color: #ffffff;
    }}

    QTableWidget:focus {{
        outline: none;
        border: 1px solid #CBD5E1;
    }}

    QHeaderView::section {{
        background-color: #082F49;
        color: #ffffff;
        padding: 10px 8px;
        border: none;
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
    }}

    /* ========================================
       INPUTS
       ======================================== */

    QLineEdit, QSpinBox, QDoubleSpinBox {{
        background-color: white;
        border: 2px solid #ddd;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
    }}

    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 2px solid {COLORS['primary']};
    }}

    /* ========================================
       COMBOBOX (DROPDOWN)
       ======================================== */

    QComboBox {{
        background-color: white;
        border: 2px solid #CBD5E1;
        border-radius: 8px;
        padding: 8px 12px;
        padding-right: 30px;
        font-size: 13px;
        font-family: "Segoe UI", sans-serif;
        color: #1e293b;
        min-height: 24px;
    }}

    QComboBox:hover {{
        border: 2px solid #38bdf8;
        background-color: #F8FAFC;
    }}

    QComboBox:focus {{
        border: 2px solid {COLORS['primary']};
        background-color: white;
    }}

    QComboBox:disabled {{
        background-color: #F1F5F9;
        color: #94A3B8;
        border: 2px solid #E2E8F0;
    }}

    /* Dropdown arrow button */
    QComboBox::drop-down {{
        border: none;
        width: 30px;
        background: transparent;
    }}

    /* Dropdown arrow icon */
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid #1e293b;
        margin-right: 8px;
    }}

    QComboBox::down-arrow:hover {{
        border-top-color: #38bdf8;
    }}

    QComboBox::down-arrow:disabled {{
        border-top-color: #94A3B8;
    }}

    /* Dropdown popup list */
    QComboBox QAbstractItemView {{
        background-color: white;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        padding: 4px;
        outline: none;
        selection-background-color: #38bdf8;
        selection-color: white;
        color: #1e293b;
        font-size: 13px;
        font-family: "Segoe UI", sans-serif;
    }}

    QComboBox QAbstractItemView::item {{
        padding: 8px 12px;
        border-radius: 6px;
        min-height: 32px;
        color: #1e293b;
    }}

    QComboBox QAbstractItemView::item:hover {{
        background-color: #E0F2FE;
        color: #0c4a6e;
    }}

    QComboBox QAbstractItemView::item:selected {{
        background-color: #38bdf8;
        color: white;
    }}

    QComboBox QAbstractItemView::item:selected:hover {{
        background-color: #0EA5E9;
        color: white;
    }}

    /* ========================================
       GROUP BOX
       ======================================== */

    QGroupBox {{
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 16px;
        font-weight: 600;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 12px;
        color: {COLORS['text_dark']};
    }}

    /* ========================================
       LABELS
       ======================================== */

    QLabel#pageTitle {{
        font-size: 24px;
        font-weight: 600;
        color: {COLORS['text_dark']};
    }}

    QLabel#sectionTitle {{
        font-size: 16px;
        font-weight: 600;
        color: {COLORS['text_dark']};
    }}

    QLabel#totalLabel {{
        font-size: 36px;
        font-weight: 700;
        color: {COLORS['success']};
    }}

    /* ========================================
       SCROLLBAR
       ======================================== */

    QScrollBar:vertical {{
        background-color: #f0f0f0;
        width: 12px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {COLORS['primary']};
        border-radius: 6px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['primary_dark']};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* ========================================
       CATEGORY TABS
       ======================================== */

    QPushButton#categoryTab {{
        background-color: transparent;
        color: {COLORS['text_muted']};
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-size: 12px;
        font-weight: 500;
    }}

    QPushButton#categoryTab:hover {{
        background-color: rgba(107, 184, 201, 0.1);
        color: {COLORS['primary']};
    }}

    QPushButton#categoryTab:checked {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_dark']};
        font-weight: 600;
    }}
    """
