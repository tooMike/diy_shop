from django import template

from shopping_cart.models import ShoppingCart

register = template.Library()


@register.simple_tag
def product_count(request):
    """Метод для передачи количества товаров в корзине."""
    cart = ShoppingCart.objects.filter(
        user=request.user
    )
    if cart.exists():
        return cart.total_quantity()
    return 0


@register.filter
def total_saving(item):
    return (item.product.price - item.product.actual_price) * item.quantity