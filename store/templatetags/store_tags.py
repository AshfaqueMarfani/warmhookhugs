"""
Warm Hook Hugs — Custom Template Tags
=======================================
"""

from django import template

register = template.Library()


@register.filter
def pkr(value):
    """Format a number as PKR currency: PKR 2,500.00"""
    try:
        return f'PKR {float(value):,.2f}'
    except (ValueError, TypeError):
        return value


@register.filter
def multiply(value, arg):
    """Multiply two values."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
