# -*- coding: utf-8 -*-
"""

Application Constants
=====================
"""

# Application Info
APP_NAME = "Profel Savdo"
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
    # Background
    'bg_main': '#e8f4f7',

    # Dark panels
    'dark_panel': '#102331',
    'dark_panel_alt': '#13293a',

    # Primary cyan
    'primary': '#6bb8c9',
    'primary_dark': '#4ca5b8',

    # Accent
    'accent': '#2f89fc',

    # Text
    'text_dark': '#0f172a',
    'text_light': '#f8fafc',
    'text_muted': '#64748b',

    # Status colors
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
    {"name": "Profil", "color": "#3498db", "icon": "📐"},
    {"name": "Ruchka", "color": "#e74c3c", "icon": "🔧"},
    {"name": "Qulf", "color": "#f39c12", "icon": "🔒"},
    {"name": "Setka", "color": "#27ae60", "icon": "🕸️"},
    {"name": "Boshqa", "color": "#95a5a6", "icon": "📦"},
]
