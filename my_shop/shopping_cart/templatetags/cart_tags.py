from django import template

from shopping_cart.models import ShoppingCart

register = template.Library()


@register.simple_tag
def product_count(request):
    """Метод для передачи количества товаров в корзине."""
    if request.user.is_authenticated:
        cart = ShoppingCart.objects.filter(user=request.user)
    else:
        if request.session.session_key:
            cart = ShoppingCart.objects.filter(
                session_key=request.session.session_key
            )
        else:
            return 0
    if cart.exists():
        return cart.total_quantity()
    return 0


@register.simple_tag
def products_in_user_shopping_carts(request):
    """
    Добавляем в контекст словарь с {id_товара: количество_в_корзине, ...}
    текущего пользователя для проверки в шаблоне,
    есть ли конкретный товар в корзине пользователя
    и отображения количества товара в корзине
    """
    users_shopping_carts = ShoppingCart.objects.all().select_related(
        "product"
    )
    # Для авторизированного пользователя фильтруем по user
    if request.user.is_authenticated:
        users_shopping_carts = users_shopping_carts.filter(
            user=request.user
        )
    # Для анонимного пользователя фильтруем по session_key
    else:
        users_shopping_carts = users_shopping_carts.filter(
            session_key=request.session.session_key
        )
    # Формируем словарь {id_товара: количество_в_корзине, ...}
    result = {}
    for cart in users_shopping_carts:
        result[cart.product.id] = cart.quantity

    return result


@register.filter
def total_saving(item):
    """Метод для получения суммарной экономии по каждой позиции в корзине."""
    return (item.product.price - item.product.actual_price) * item.quantity


@register.filter
def get_quantity_from_product_dict(product_dict, product):
    """Метод для извлечения значения по ключу из словаря в шаблоне."""
    return product_dict.get(product, 0)
