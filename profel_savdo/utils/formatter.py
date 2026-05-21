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


def format_decimal(value, decimals=2):
    """Format numeric value without unnecessary trailing zeros."""
    if value is None:
        return "0"
    return f"{float(value):.{decimals}f}".rstrip('0').rstrip('.')


def format_quantity(value, unit):
    """
    Format quantity based on unit type
    """
    if value is None:
        value = 0
    if not unit:
        unit = "dona"

    unit_lower = unit.lower().strip()

    if unit_lower in INTEGER_UNITS:
        return f"{int(float(value))} {unit}"
    else:
        formatted = format_decimal(value)
        return f"{formatted} {unit}"


def format_quantity_display(value, unit):
    """
    Format quantity for display in tables (without unit)
    """
    if value is None:
        value = 0
    if not unit:
        unit = "dona"

    unit_lower = unit.lower().strip()

    if unit_lower in INTEGER_UNITS:
        return str(int(float(value)))
    else:
        return format_decimal(value)


def calculate_area_sqm(width, height):
    """Calculate area in square meters."""
    return round(float(width or 0) * float(height or 0), 4)


def calculate_kvm(eni, boyi):
    """Calculate glass area from width and height in meters."""
    return calculate_area_sqm(eni, boyi)


def parse_decimal(value, field_name, allow_zero=False):
    """Parse decimal input and raise a user-friendly validation message."""
    try:
        normalized = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} noto'g'ri kiritilgan")

    if allow_zero:
        if normalized < 0:
            raise ValueError(f"{field_name} manfiy bo'lishi mumkin emas")
    elif normalized <= 0:
        raise ValueError(f"{field_name} 0 dan katta bo'lishi kerak")
    return normalized


def validate_positive_decimal(value, field_name):
    """Return a positive decimal value or raise a user-friendly error."""
    return parse_decimal(value, field_name, allow_zero=False)


def calculate_window_metrics(eni, boyi, narx_per_kvm=None):
    """Calculate normalized dimensions, KVM, and optional line total."""
    normalized_eni = validate_positive_decimal(eni, "Eni")
    normalized_boyi = validate_positive_decimal(boyi, "Bo'yi")
    kvm = calculate_kvm(normalized_eni, normalized_boyi)

    metrics = {
        'eni': normalized_eni,
        'boyi': normalized_boyi,
        'kvm': kvm,
        'width': normalized_eni,
        'height': normalized_boyi,
        'area_sqm': kvm,
    }

    if narx_per_kvm is not None:
        normalized_price = validate_positive_decimal(narx_per_kvm, "Narx/KVM")
        metrics['narx_per_kvm'] = normalized_price
        metrics['price'] = normalized_price
        metrics['jami'] = round(kvm * normalized_price, 2)

    return metrics


def resolve_kvm_fields(data):
    """Resolve Uzbek and legacy dimension keys into one compatible payload."""
    eni = data.get('eni', data.get('width'))
    boyi = data.get('boyi', data.get('height'))
    kvm = data.get('kvm', data.get('area_sqm'))

    if eni is not None and boyi is not None:
        metrics = calculate_window_metrics(eni, boyi)
        eni = metrics['eni']
        boyi = metrics['boyi']
        kvm = metrics['kvm']
    elif kvm is not None:
        kvm = parse_decimal(kvm, "KVM")

    narx_per_kvm = data.get('narx_per_kvm', data.get('price'))
    return {
        'eni': eni,
        'boyi': boyi,
        'kvm': kvm,
        'width': eni,
        'height': boyi,
        'area_sqm': kvm,
        'narx_per_kvm': narx_per_kvm,
        'price': narx_per_kvm,
    }


def format_meters(value):
    """Format dimension in meters."""
    return f"{format_decimal(value)} m"


def format_square_meters(value):
    """Format area in square meters."""
    return f"{format_decimal(value)} kvm"


def format_window_size(width, height, area_sqm=None):
    """Format window dimensions and area in a compact string."""
    resolved_area = calculate_area_sqm(width, height) if area_sqm is None else float(area_sqm or 0)
    if not width or not height:
        return format_square_meters(resolved_area)
    return f"{format_meters(width)} x {format_meters(height)} ({format_square_meters(resolved_area)})"


def format_window_sale_line(product_name, width, height, area_sqm, price_per_sqm):
    """Format one sold window line for reports and customer history."""
    size_text = format_window_size(width, height, area_sqm)
    return (
        f"{product_name} | {size_text} | Narx/KVM: {float(price_per_sqm):,.0f} so'm"
    )
