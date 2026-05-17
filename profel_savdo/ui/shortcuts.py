# -*- coding: utf-8 -*-
"""
Keyboard Shortcuts Manager
"""
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt


class ShortcutManager:
    """Centralized keyboard shortcuts management"""

    SHORTCUTS = {
        # Navigation
        'F1': 'Sotuv',
        'F2': 'Mahsulotlar',
        'F3': 'Mijozlar',
        'F4': 'Hisobot',
        'F5': 'Qarz To\'lash',
        'F6': 'Kategoriyalar',
        'F7': 'Sozlamalar',
        'F8': 'Hisob-Chek',
        'F9': 'Savatni Tozalash',
        'F12': 'Savdoni Yakunlash',

        # Actions
        'Ctrl+F': 'Qidirish',
        'Ctrl+P': 'Chop etish',
        'Ctrl+E': 'Excel export',
        'Delete': 'O\'chirish',
        'Enter': 'Tasdiqlash',
        'Esc': 'Bekor qilish',
    }

    @staticmethod
    def setup_main_window_shortcuts(main_window):
        """Setup main window shortcuts"""
        # F1-F12 navigation
        QShortcut(QKeySequence("F1"), main_window).activated.connect(lambda: main_window.switch_page(0))
        QShortcut(QKeySequence("F2"), main_window).activated.connect(lambda: main_window.switch_page(1))
        QShortcut(QKeySequence("F3"), main_window).activated.connect(lambda: main_window.switch_page(2))
        QShortcut(QKeySequence("F4"), main_window).activated.connect(lambda: main_window.switch_page(3))
        QShortcut(QKeySequence("F5"), main_window).activated.connect(lambda: main_window.switch_page(4))
        QShortcut(QKeySequence("F6"), main_window).activated.connect(lambda: main_window.switch_page(5))
        QShortcut(QKeySequence("F7"), main_window).activated.connect(lambda: main_window.switch_page(6))

    @staticmethod
    def setup_page_shortcuts(page):
        """Setup common page shortcuts"""
        # Ctrl+F for search
        if hasattr(page, 'search_input'):
            QShortcut(QKeySequence("Ctrl+F"), page).activated.connect(
                lambda: page.search_input.setFocus()
            )

    @staticmethod
    def get_shortcut_help_text():
        """Get formatted shortcut help text"""
        lines = ["KLAVIATURA YORLIQLARI:\n"]
        for key, desc in ShortcutManager.SHORTCUTS.items():
            lines.append(f"{key:15} - {desc}")
        return "\n".join(lines)
