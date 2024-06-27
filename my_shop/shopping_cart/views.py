from django.shortcuts import render, redirect

from main.models import Product
from shopping_cart.models import ShoppingCart


def show_cart(request):
    """Отображение товаров в корзине."""

    shopping_carts = ShoppingCart.objects.filter(
        user=request.user
    ).prefetch_related("product")
    context = {"cart": shopping_carts}

    return render(request, "shopping_cart/cart.html", context=context)


def cart_add(request, product_id):
    """Добавление товаров в корзину."""

    product = Product.objects.get(id=product_id)

    if request.user.is_authenticated:
        cart = ShoppingCart.objects.filter(user=request.user, product=product)

        if cart.exists():
            cart = cart.first()
            cart.quantity += 1
            cart.save()
        else:
            ShoppingCart.objects.create(
                user=request.user, product=product, quantity=1
            )
    return redirect(request.META["HTTP_REFERER"])


def cart_change(request, product_id):
    """Изменение корзины."""

    product = Product.objects.get(id=product_id)

    if request.user.is_authenticated:
        cart = ShoppingCart.objects.filter(user=request.user, product=product)

        if cart.exists():
            cart = cart.first()
            cart.quantity -= 1
            # Если количество товара в корзине становится равным 0,
            # то удаляем этот товар из корзины
            if cart.quantity == 0:
                cart_remove(request, product_id)
                return redirect(request.META["HTTP_REFERER"])
            cart.save()

    return redirect(request.META["HTTP_REFERER"])


def cart_remove(request, product_id):
    """Удаление товаров из корзины."""
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        cart = ShoppingCart.objects.filter(user=request.user, product=product)
        if cart.exists():
            cart.delete()
    return redirect(request.META["HTTP_REFERER"])
