# -*- coding: utf-8 -*-
"""
Application Constants
=====================
"""

# Application Info
APP_NAME = "OYNA SAVDO"
APP_VERSION = "1.0.0"
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"
WINDOW_MIN_WIDTH = 1400
WINDOW_MIN_HEIGHT = 800

# Database
DATABASE_FILE = "profel_savdo.db"

# Business Rules
DEBT_LIMIT = 10000000  # 10 million so'm

# Color System
COLORS = {
    'bg_main': '#e8f4f7',
    'dark_panel': '#102331',
    'dark_panel_alt': '#13293a',
    'primary': '#6bb8c9',
    'primary_dark': '#4ca5b8',
    'accent': '#2f89fc',
    'text_dark': '#0f172a',
    'text_light': '#f8fafc',
    'text_muted': '#64748b',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db',
}

# Typography
FONT_FAMILY = "Segoe UI"
FONT_SIZE_SMALL = 11
FONT_SIZE_NORMAL = 12
FONT_SIZE_MEDIUM = 14
FONT_SIZE_LARGE = 18
FONT_SIZE_XLARGE = 24
FONT_SIZE_TOTAL = 36

# Categories
DEFAULT_CATEGORIES = [
    {"name": "Shaffof", "color": "#3498db", "icon": "[]"},
    {"name": "Bronza", "color": "#b45309", "icon": "[]"},
    {"name": "Matoviy", "color": "#64748b", "icon": "[]"},
    {"name": "Vitraj", "color": "#0f766e", "icon": "[]"},
    {"name": "Boshqa", "color": "#95a5a6", "icon": "[]"},
]
