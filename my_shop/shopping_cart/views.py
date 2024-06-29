from django.shortcuts import redirect, render

from main.models import Product
from shopping_cart.models import ShoppingCart


def show_cart(request):
    """Отображение товаров в корзине."""

    if request.user.is_authenticated:
        shopping_carts = ShoppingCart.objects.filter(
            user=request.user
        ).prefetch_related("product")
        context = {"carts": shopping_carts}
    else:
        shopping_carts = (
            ShoppingCart.objects.exclude(session_key=None)
            .filter(session_key=request.session.session_key)
            .prefetch_related("product")
        )
        context = {"carts": shopping_carts}

    return render(request, "shopping_cart/cart.html", context=context)


def cart_add(request, product_id):
    """Добавление товаров в корзину."""

    product = Product.objects.get(id=product_id)

    if request.user.is_authenticated:
        cart = ShoppingCart.objects.filter(
            user=request.user,
            product=product,
        )
    else:
        # Добавляем неавторизированному пользователю
        # сессионный ключ, если его нет
        if not request.session.session_key:
            request.session.create()

        cart = ShoppingCart.objects.filter(
            session_key=request.session.session_key, product=product
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
                product=product,
                quantity=1,
            )
        else:
            ShoppingCart.objects.create(
                session_key=request.session.session_key,
                product=product,
                quantity=1,
            )
    return redirect(request.META["HTTP_REFERER"])


def cart_change(request, product_id):
    """Изменение корзины."""

    product = Product.objects.get(id=product_id)

    if request.user.is_authenticated:
        cart = ShoppingCart.objects.filter(user=request.user, product=product)
    else:
        cart = ShoppingCart.objects.filter(
            session_key=request.session.session_key, product=product
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

    cart = ShoppingCart.objects.get(id=cart_id)
    cart.delete()
    return redirect(request.META["HTTP_REFERER"])
