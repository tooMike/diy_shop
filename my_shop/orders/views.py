from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.forms import ValidationError
from django.shortcuts import redirect, render

from main.models import ColorProductShop, Shop
from orders.forms import CreateOrderForm
from orders.models import Order, OrderProduct
from shopping_cart.models import ShoppingCart


@login_required
def create_order(request):
    """Создание заказа."""
    initial = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
    }
    form = CreateOrderForm(data=request.POST or None, initial=initial)
    carts = ShoppingCart.objects.filter(user=request.user).select_related(
        "product",
        "colorproduct",
        "colorproduct__color",
    )
    stores = Shop.objects.exclude(name__icontains="Склад")
    context = {
        "carts": carts,
        "form": form,
        "stores": stores,
    }
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user = request.user

                if carts.exists():
                    requires_delivery = (
                        form.cleaned_data["requires_delivery"] == "true"
                    )
                    payment_on_get = (
                        form.cleaned_data["payment_on_get"] == "true"
                    )
                    if requires_delivery:
                        order = Order.objects.create(
                            user=user,
                            phone=form.cleaned_data["phone"],
                            requires_delivery=requires_delivery,
                            delivery_city=form.cleaned_data["delivery_city"],
                            delivery_adress=form.cleaned_data[
                                "delivery_adress"
                            ],
                            payment_on_get=payment_on_get,
                        )
                    else:
                        order = Order.objects.create(
                            user=user,
                            phone=form.cleaned_data["phone"],
                            requires_delivery=requires_delivery,
                            shop=form.cleaned_data["shop"],
                            payment_on_get=payment_on_get,
                        )

                    # Одним запросом получаем доступное количество
                    # товаров в выбранном магазине
                    available_products = ColorProductShop.objects.filter(
                        colorproduct__shoppingcart__user=user,
                        shop=form.cleaned_data["shop"],
                    ).annotate(total=Sum("quantity"))

                    # Проверяем, есть ли вообще товары в наличии
                    # в выбранном магазине
                    if not available_products:
                        raise ValidationError(
                            "В выбранном магазине товары отсутствуют. \
                            Выберите другой магазин."
                        )

                    # Формируем словарь формата {"colorproduct": quantity}
                    product_quantities = {}
                    for product in available_products:
                        product_quantities[product.colorproduct_id] = product

                    # Формируем записи OrderProduct
                    orderproduct = []
                    shop_quantity = []
                    for item in carts:
                        product_quantity = product_quantities.get(
                            item.colorproduct.id, None
                        )
                        # Проверяем доступен ли конкретный товар
                        # в выбранном магазине
                        if product_quantity is None:
                            raise ValidationError(
                                f"В выбранном магазине товар {item.product} отсутствует. \
                                Выберите другой магазин."
                            )
                        if product_quantity.total < item.quantity:
                            raise ValidationError(
                                f"Недостаточное количество товаров: \
                                    {item.product}: {item.colorproduct}. \
                                    В наличии: {product_quantity.total}"
                            )
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

                    # Обновляем наличие в магазинах для всех позиций в заказе
                    ColorProductShop.objects.bulk_update(
                        shop_quantity, ["quantity"]
                    )

                    # Создаем записи в БД для всех позиций в заказе
                    OrderProduct.objects.bulk_create(orderproduct)

                    # Очищаем корзину пользователя
                    carts.delete()

                    messages.success(request, "Заказ оформлен")
                    return redirect("main:index")

        # Передаем сообщение об ошибке на страницу заказа
        except ValidationError as e:
            messages.error(request, e.message)
            return redirect("order:create_order")

    return render(
        request, template_name="orders/create_order.html", context=context
    )
