from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api import views

router = SimpleRouter()
router.register('products',  views.ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
