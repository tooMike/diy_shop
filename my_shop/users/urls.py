from django.urls import path

from users import views


app_name = 'users'

urlpatterns = [
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='profile'),
    path('', views.UserRegistration.as_view(), name='registration')

]
