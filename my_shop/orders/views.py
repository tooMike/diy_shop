from django.shortcuts import render

from main.models import Shop
from shopping_cart.models import ShoppingCart


def create_order(request):
    if request.user.is_authenticated:
        carts = ShoppingCart.objects.filter(user=request.user)
    else:
        carts = ShoppingCart.objects.filter(
            session_key=request.session.session_key
        ).select_related("product")
    stores = Shop.objects.all()
    context = {"carts": carts, "stores": stores}
    return render(
        request, template_name="orders/create_order.html", context=context
    )
