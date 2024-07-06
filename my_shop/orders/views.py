from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from main.models import ColorProductShop, Shop
from orders.forms import CreateOrderForm
from orders.models import Order, OrderProduct
from orders.utils import (get_available_products, prepare_order_products,
                          update_user_info, validate_cart_items)
from shopping_cart.models import ShoppingCart


@login_required
def create_order(request):
    """Создание заказа."""
    initial = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "phone": request.user.phone,
    }
    form = CreateOrderForm(data=request.POST or None, initial=initial)
    carts = ShoppingCart.objects.filter(user=request.user).select_related(
        "product",
        "colorproduct",
        "colorproduct__color",
    )
    shops = Shop.objects.exclude(name__icontains="Склад")
    context = {
        "carts": carts,
        "form": form,
        "shops": shops,
    }
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user = request.user

                # Сохраняем данные в модель пользователя,
                # если этих данных еще нет
                update_user_info(user=user, cleaned_data=form.cleaned_data)

                if carts.exists():
                    requires_delivery = (
                        form.cleaned_data["requires_delivery"] == "true"
                    )
                    payment_on_get = (
                        form.cleaned_data["payment_on_get"] == "true"
                    )
                    if requires_delivery:
                        shop = get_object_or_404(Shop, name__icontains="Склад")
                    else:
                        shop = form.cleaned_data["shop"]

                    # Проверяем, есть ли товары из корзины пользователя
                    # в наличии в выбранном магазине
                    product_quantities = get_available_products(
                        user=user, shop=shop
                    )
                    # Проверяем наличие каждого товара в выбранного магазине
                    validate_cart_items(carts, product_quantities)

                    # Если проверки успешно прошли, то создаем заказ
                    order_data = {
                        "user": user,
                        "phone": form.cleaned_data["phone"],
                        "requires_delivery": requires_delivery,
                        "shop": shop,
                        "payment_on_get": payment_on_get,
                    }
                    if requires_delivery:
                        order_data["delivery_city"] = form.cleaned_data[
                            "delivery_city"
                        ]
                        order_data["delivery_adress"] = form.cleaned_data[
                            "delivery_adress"
                        ]
                    order = Order.objects.create(**order_data)

                    # Формируем список товаров для этого заказа
                    # и список нового наличия в магазинах
                    orderproduct, shop_quantity = prepare_order_products(
                        carts, product_quantities, order
                    )

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
