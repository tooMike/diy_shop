from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api import views as api_view


router = SimpleRouter()
router.register('products',  api_view.ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/email_verification/', api_view.email_send_confirmation_code, name='email_send_confirmation_code'),
    path('auth/sign_up/', api_view.user_signup, name='user_signup'),
    path('auth/token/', api_view.get_token, name='user_get_token')
]
