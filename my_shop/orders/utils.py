from django.db.models import Sum
from django.forms import ValidationError
from main.models import ColorProductShop
from orders.models import OrderProduct


def get_available_products(user, shop):
    """
    Метод для получения информации о товаре в магазине в формате
    {"colorproduct_id": Product()}.
    """

    # Одним запросом получаем доступное количество
    # товаров в выбранном магазине
    available_products = ColorProductShop.objects.filter(
        colorproduct__shoppingcart__user=user,
        shop=shop,
    ).annotate(total=Sum("quantity"))

    # Формируем словарь формата {"colorproduct_id": Product()}
    product_quantities = {}
    for product in available_products:
        product_quantities[product.colorproduct_id] = product

    return product_quantities


def update_user_info(user, cleaned_data):
    """Метод для обновления данных пользователя."""
    if not user.first_name:
        user.first_name = cleaned_data["first_name"]
    if not user.last_name:
        user.last_name = cleaned_data["last_name"]
    if not user.phone:
        user.phone = cleaned_data["phone"]
    user.save()


def validate_cart_items(carts, product_quantities):
    """Метод для проверки наличия товаров из корзины в магазине."""
    for item in carts:
        product_quantity = product_quantities.get(item.colorproduct_id)
        # Проверяем доступен ли конкретный товар в выбранном магазине
        if not product_quantity:
            raise ValidationError(
                f"В выбранном магазине товар {item.product} \
                {item.colorproduct} отсутствует. Выберите другой магазин."
            )
        if product_quantity.total < item.quantity:
            raise ValidationError(
                f"Недостаточное количество товаров: {item.product}: \
                 {item.colorproduct}. В наличии: {product_quantity.total}"
            )


def prepare_order_products(carts, product_quantities, order):
    """
    Метод для формирования списка товаров в заказе
    и списка с новым количеством товаров в магазине.
    """
    orderproduct = []
    shop_quantity = []
    for item in carts:
        product_quantity = product_quantities.get(item.colorproduct.id, None)
        orderproduct.append(
            OrderProduct(
                order=order,
                product=item.product,
                colorproduct=item.colorproduct,
                price=item.product.actual_price,
                quantity=item.quantity,
            )
        )

        # Обновляем наличие товара в выбранном магазину
        product_quantity.quantity -= item.quantity
        # Формируем список для bulk_update
        shop_quantity.append(product_quantity)

    return orderproduct, shop_quantity
