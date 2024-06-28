from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from users.views import UserLoginView

handler404 = "pages.views.page_not_found"
handler500 = "pages.views.server_error"

schema_view = get_schema_view(
    openapi.Info(
        title="DIY shop API",
        default_version="v1",
        description="Документация для приложения DIY shop",
        # terms_of_service="URL страницы с пользовательским соглашением",
        contact=openapi.Contact(email="admin@diy_shop.ru"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/login/", UserLoginView.as_view(), name="login"),
    path("auth/", include("django.contrib.auth.urls")),
    path("user/", include("users.urls")),
    path("pages/", include("pages.urls")),
    path("api/", include("api.urls")),
    path("card/", include("shopping_cart.urls")),
    path("", include("main.urls")),
]

urlpatterns += [
    url(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    url(
        r"^redoc/$",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]

# Подключаем дебаг-панель:
if settings.DEBUG:
    import debug_toolbar

    # Добавить к списку urlpatterns список адресов
    # из приложения debug_toolbar:
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
# Подключаем функцию static() к urlpatterns:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
