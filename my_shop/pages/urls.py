from django.urls import path

from pages import views

app_name = "pages"

urlpatterns = [path("about/", views.AboutView.as_view(), name="about")]
