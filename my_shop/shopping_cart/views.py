from django.shortcuts import render


def cart(request):
    return render(request, 'shopping_cart/cart.html')


def cart_add(request, product_id):
    pass


def cart_change(request, product_id):
    pass


def cart_remove(request, product_id):
    pass
