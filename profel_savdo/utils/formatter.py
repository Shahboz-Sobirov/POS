# -*- coding: utf-8 -*-
"""
Quantity Formatter Utility
"""

# Integer units - no decimal places
INTEGER_UNITS = [
    "dona",
    "sht",
    "pcs",
    "ta",
    "don",
    "piece",
    "pieces",
]


def format_quantity(value, unit):
    """
    Format quantity based on unit type

    Args:
        value: Quantity value (float or int)
        unit: Unit name (str)

    Returns:
        Formatted string with quantity and unit

    Examples:
        format_quantity(50.00, "dona") -> "50 dona"
        format_quantity(100.00, "sht") -> "100 sht"
        format_quantity(12.5, "metr") -> "12.5 metr"
        format_quantity(2.75, "m2") -> "2.75 m2"
    """
    if not unit:
        unit = "dona"

    unit_lower = unit.lower().strip()

    # Check if unit requires integer format
    if unit_lower in INTEGER_UNITS:
        # Format as integer
        return f"{int(value)} {unit}"
    else:
        # Format with decimals (remove trailing zeros)
        formatted = f"{value:.2f}".rstrip('0').rstrip('.')
        return f"{formatted} {unit}"


def format_quantity_display(value, unit):
    """
    Format quantity for display in tables (without unit)

    Args:
        value: Quantity value (float or int)
        unit: Unit name (str)

    Returns:
        Formatted quantity string

    Examples:
        format_quantity_display(50.00, "dona") -> "50"
        format_quantity_display(12.5, "metr") -> "12.5"
    """
    if not unit:
        unit = "dona"

    unit_lower = unit.lower().strip()

    # Check if unit requires integer format
    if unit_lower in INTEGER_UNITS:
        return str(int(value))
    else:
        # Format with decimals (remove trailing zeros)
        return f"{value:.2f}".rstrip('0').rstrip('.')
