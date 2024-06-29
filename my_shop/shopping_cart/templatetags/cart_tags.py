from django import template

from shopping_cart.models import ShoppingCart

register = template.Library()


@register.simple_tag
def product_count(request):
    """Метод для передачи количества товаров в корзине."""
    if request.user.is_authenticated:
        cart = ShoppingCart.objects.filter(user=request.user)
    else:
        cart = ShoppingCart.objects.filter(
            session_key=request.session.session_key
        )
    if cart.exists():
        return cart.total_quantity()
    return 0


@register.filter
def total_saving(item):
    """Метод для получения суммарной экономии по каждой позиции в корзине."""
    return (item.product.price - item.product.actual_price) * item.quantity


@register.filter
def get_quantity_from_product_dict(product_dict, product):
    """Метод для извлечения значения по ключу из словаря в шаблоне."""
    return product_dict.get(product, 0)
