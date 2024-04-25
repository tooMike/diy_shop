from django.urls import path

from users import views


app_name = 'users'

urlpatterns = [
    path('profile_edit/', views.UserProfileView.as_view(), name='profile'),
    path('registration/', views.UserRegistration.as_view(), name='registration')
]
