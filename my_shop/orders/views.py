from django.shortcuts import render
from django.db import transaction

from main.models import Shop
from orders.forms import CreateOrderForm
from shopping_cart.models import ShoppingCart


def create_order(request):
    """Создание заказа."""
    context = {}
    if request.method == 'POST':
        form = CreateOrderForm(data=request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = request.user
            except:
                pass

    else:
        if request.user.is_authenticated:
            carts = ShoppingCart.objects.filter(user=request.user)
            initial = {
                'first_name': request.user.first_name,
                'second_name': request.user.second_name,
            }
        else:
            carts = ShoppingCart.objects.filter(
                session_key=request.session.session_key
            ).select_related("product")
            initial = {}
        stores = Shop.objects.all()
        form = CreateOrderForm(initial=initial)

        context["carts"] = carts
        context["stores"] = stores

    context["form"] = form

    return render(
        request, template_name="orders/create_order.html", context=context
    )
