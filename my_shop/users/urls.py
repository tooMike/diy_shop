from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("profile_edit/", views.UserProfileView.as_view(), name="profile"),
    path(
        "registration/email_verification",
        views.email_verification,
        name="email_verification",
    ),
    path(
        "registration/code_verification",
        views.code_verification,
        name="code_verification",
    ),
    path(
        "registration/", views.UserRegistration.as_view(), name="registration"
    ),
]
