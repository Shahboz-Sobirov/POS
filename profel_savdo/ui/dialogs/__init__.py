# -*- coding: utf-8 -*-
"""
UI Dialogs
"""
from .error_dialog import ErrorDialog, show_error
from .customer_profile_dialog import CustomerProfileDialog
from .glass_order_dialog import GlassOrderDialog, WindowCalculationSummary

__all__ = [
    'ErrorDialog',
    'show_error',
    'CustomerProfileDialog',
    'GlassOrderDialog',
    'WindowCalculationSummary',
]
