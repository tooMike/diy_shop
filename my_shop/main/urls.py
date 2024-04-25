from django.contrib import admin
from django.urls import include, path

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='index'),
    path('product/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:category_slug>/', views.CategoryListView.as_view(), name='category'),
    path('manufacturer/<slug:manufacturer_slug>/', views.ManufacturerListView.as_view(), name='manufacturer'),
]