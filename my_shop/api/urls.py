from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api import views as api_view

router_v1 = SimpleRouter()
router_v1.register(
    "categories", api_view.CategoriesViewSet, basename="categories"
)
router_v1.register(
    "manufacturer", api_view.ManufacrurerViewSet, basename="manufacturer"
)
router_v1.register(
    r"product/(?P<product_id>\d+)/reviews",
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
    path(
        "product/<int:product_id>/",
        api_view.ProductViewSet.as_view({"get": "retrieve"}),
        name="product_detail",
    ),
    path(
        "products/",
        api_view.ProductsListViewSet.as_view({"get": "list"}),
        name="products_list",
    ),
    path("", include(router_v1.urls)),
]
