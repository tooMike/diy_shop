from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api import views as api_view


router = SimpleRouter()
router.register('products',  api_view.ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.base')),
    path('auth/', include('djoser.urls.jwt')),
]
