from django.urls import path

from shopping_cart import views

app_name = "cart"

urlpatterns = [
    path("cart/", views.show_cart, name="cart"),
    path("cart_add/", views.cart_add, name="cart_add"),
    path(
        "cart_change/<int:product_id>/<int:colorproduct_id>/",
        views.cart_change,
        name="cart_change",
    ),
    path(
        "cart_remove/<int:cart_id>",
        views.cart_remove,
        name="cart_remove",
    ),
]
