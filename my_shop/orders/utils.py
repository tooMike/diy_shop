from django.db.models import Sum

from main.models import ColorProductShop


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
