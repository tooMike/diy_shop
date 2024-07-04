from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from main.models import ColorProductShop, Shop
from orders.forms import CreateOrderForm
from orders.models import Order, OrderProduct
from orders.utils import get_available_products
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
                if not user.first_name:
                    user.first_name = form.cleaned_data["first_name"]
                if not user.last_name:
                    user.last_name = form.cleaned_data["last_name"]
                if not user.phone:
                    user.phone = form.cleaned_data["phone"]
                user.save()

                if carts.exists():
                    requires_delivery = (
                        form.cleaned_data["requires_delivery"] == "true"
                    )
                    payment_on_get = (
                        form.cleaned_data["payment_on_get"] == "true"
                    )
                    if requires_delivery:
                        shop = get_object_or_404(Shop, name__icontains="Склад")

                        order = Order.objects.create(
                            user=user,
                            phone=form.cleaned_data["phone"],
                            requires_delivery=requires_delivery,
                            delivery_city=form.cleaned_data["delivery_city"],
                            delivery_adress=form.cleaned_data[
                                "delivery_adress"
                            ],
                            shop=shop,
                            payment_on_get=payment_on_get,
                        )
                    else:
                        shop = form.cleaned_data["shop"]
                        order = Order.objects.create(
                            user=user,
                            phone=form.cleaned_data["phone"],
                            requires_delivery=requires_delivery,
                            shop=shop,
                            payment_on_get=payment_on_get,
                        )

                    # Проверяем, есть ли товары из корзины пользователя
                    # в наличии в выбранном магазине
                    product_quantities = get_available_products(
                        user=user, shop=shop
                    )
                    if not product_quantities:
                        raise ValidationError(
                            "В выбранном магазине товары отсутствуют. \
                            Выберите другой магазин."
                        )

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
                                f"В выбранном магазине товар {item.product} \
                                отсутствует. Выберите другой магазин."
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
