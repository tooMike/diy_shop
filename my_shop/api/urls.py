from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api import views as api_view

router_v1 = SimpleRouter()
router_v1.register(
    "categories", api_view.CategoriesViewSet, basename="categories"
)
router_v1.register(
    "manufacturer", api_view.ManufacturerViewSet, basename="manufacturer"
)
router_v1.register(
    "cart", api_view.ShoppingCartViewSet, basename="shopping_cart"
)
router_v1.register(
    "order", api_view.OrderViewSet, basename="order"
)
router_v1.register(
    "products", api_view.ProductsViewSet, basename="products"
)
router_v1.register(
    r"products/(?P<product_id>\d+)/reviews",
    api_view.ReviewViewSet,
    basename="review",
)

urlpatterns = [
    path(
        "auth/email_verification/",
        api_view.email_send_confirmation_code,
        name="email_send_confirmation_code",
    ),
    path("auth/sign_up/", api_view.user_signup, name="user_signup"),
    path("auth/token/", api_view.get_token, name="user_get_token"),
    path("", include(router_v1.urls)),
]
