from django.shortcuts import get_object_or_404, redirect, render

from main.models import ColorProduct
from shopping_cart.forms import CartAddForm
from shopping_cart.models import ShoppingCart


def show_cart(request):
    """Отображение товаров в корзине."""

    if request.user.is_authenticated:
        shopping_carts = ShoppingCart.objects.filter(
            user=request.user
        ).select_related("colorproduct", "colorproduct__color", "product")
    else:
        shopping_carts = (
            ShoppingCart.objects.exclude(session_key=None)
            .filter(session_key=request.session.session_key)
            .select_related("colorproduct", "colorproduct__color", "product")
        )
    context = {"carts": shopping_carts}

    return render(request, "shopping_cart/cart.html", context=context)


def cart_add(request):
    """Добавление товаров в корзину."""

    form = CartAddForm(
        request.POST or None,
    )
    if form.is_valid():
        colorproduct_id = form.cleaned_data["colorproduct_id"]
        colorproduct = get_object_or_404(ColorProduct, id=colorproduct_id)

        if request.user.is_authenticated:
            cart = ShoppingCart.objects.filter(
                user=request.user,
                colorproduct=colorproduct,
            )
        else:
            # Добавляем неавторизированному пользователю
            # сессионный ключ, если его нет
            if not request.session.session_key:
                request.session.create()

            cart = ShoppingCart.objects.filter(
                session_key=request.session.session_key,
                colorproduct=colorproduct,
            )
        if cart.exists():
            cart = cart.first()
            if cart:
                cart.quantity += 1
                cart.save()
        else:
            if request.user.is_authenticated:
                ShoppingCart.objects.create(
                    user=request.user,
                    colorproduct=colorproduct,
                    product=colorproduct.product,
                    quantity=1,
                )
            else:
                ShoppingCart.objects.create(
                    session_key=request.session.session_key,
                    colorproduct=colorproduct,
                    product=colorproduct.product,
                    quantity=1,
                )
    return redirect(request.META["HTTP_REFERER"])


def cart_change(request, colorproduct_id):
    """Изменение корзины."""

    colorproduct = get_object_or_404(ColorProduct, id=colorproduct_id)

    if request.user.is_authenticated:
        cart = ShoppingCart.objects.filter(
            user=request.user, colorproduct=colorproduct
        )
    else:
        cart = ShoppingCart.objects.filter(
            session_key=request.session.session_key,
            colorproduct=colorproduct,
        )

    if cart.exists():
        cart = cart.first()
        if cart:
            cart.quantity -= 1
            # Если количество товара в корзине становится равным 0,
            # то удаляем этот товар из корзины
            if cart.quantity == 0:
                cart_remove(request, cart.id)
                return redirect(request.META["HTTP_REFERER"])
            cart.save()

    return redirect(request.META["HTTP_REFERER"])


def cart_remove(request, cart_id):
    """Удаление позиций из корзины."""

    cart = get_object_or_404(ShoppingCart, id=cart_id)
    cart.delete()
    return redirect(request.META["HTTP_REFERER"])
