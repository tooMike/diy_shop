from django.contrib import admin
from django.urls import include, path

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='index'),
    path('product/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('product/<int:product_id>/edit_review/<int:review_id>/', views.product_detail_view, name='edit_review'),
    path('product/<int:product_id>/add_review/', views.add_review, name='add_review'),
    path('delete_review/<int:review_id>', views.delete_review, name='delete_review'),
    path('category/<slug:category_slug>/', views.CategoryListView.as_view(), name='category'),
    path('manufacturer/<slug:manufacturer_slug>/', views.ManufacturerListView.as_view(), name='manufacturer'),
]