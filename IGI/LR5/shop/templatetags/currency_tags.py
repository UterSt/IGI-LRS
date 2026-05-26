from decimal import Decimal, ROUND_HALF_UP
from django import template

register = template.Library()

@register.filter
def currency_value(value, factor):
    try:
        amount = Decimal(str(value))
        multiplier = Decimal(str(factor or 1))
        return (amount * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:  # noqa: BLE001
        return value
