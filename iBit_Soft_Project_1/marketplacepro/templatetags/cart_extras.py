from django import template

register = template.Library()


@register.filter
def calculate_cart_total(items):
    total = sum(item.product.price * item.quantity for item in items)
    return total


@register.filter(name='mul')
def mul(value, arg):
    """Multiplies value by arg."""
    try:
        return value * arg
    except (TypeError, ValueError):
        return ''
