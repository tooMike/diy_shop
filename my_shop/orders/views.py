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
        "product"
    )
    stores = Shop.objects.all()
    context = {
        "carts": carts,
        "form": form,
        "stores": stores,
    }
    if request.method == "POST":
        if form.is_valid():
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
                                delivery_city=form.cleaned_data[
                                    "delivery_city"
                                ],
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

                        orderproduct = []

                        # available_products = Color

                        for item in carts:
                            available_products = (
                                ColorProductShop.objects.filter(
                                    colorproduct__product=item.product
                                ).aggregate(total=Sum("quantity"))["total"]
                            )
                            if available_products < item.quantity:
                                raise ValidationError(
                                    f"Недостаточное количество товаров в наличии\
                                      В наличии: {available_products}"
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

                            # Здесь должно быть уменьшение количества товаров в наличии

                        # Создаем записи в БД для всех позиций в заказе
                        OrderProduct.objects.bulk_create(orderproduct)

                        # Очищаем корзину пользователя
                        carts.delete()

                        messages.success(request, "Заказ оформлен")
                        return redirect("main:index")

            except ValidationError as e:
                messages.success(request, str(e))
                return redirect("order:create_order")

    return render(
        request, template_name="orders/create_order.html", context=context
    )
