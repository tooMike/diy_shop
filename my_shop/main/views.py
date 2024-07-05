from collections import defaultdict

from django.conf import settings
from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ReviewForm
from main.models import (Category, ColorProduct, ColorProductShop,
                         Manufacturer, Product, Review)
from main.views_mixins import BaseObjectListViewMixin, ObjectListViewMixin

paginate_by = getattr(settings, "PAGINATE_BY", 10)


class ProductListView(BaseObjectListViewMixin):
    """Отображение списка товаров"""


def product_detail_view(request, product_id, review_id=None):
    """Отображение страницы товара"""
    queryset = Product.objects.annotate(
        rating=Avg("reviews__rating"),
        reviews_count=Count("reviews"),
    ).select_related("category", "manufacturer", "manufacturer__country")
    product = get_object_or_404(queryset, id=product_id, is_active=True)

    # Добавляем в контекст данные о товаре в оффлайн магазинах
    grouped_data = defaultdict(list)
    for colorproductshop in (
        ColorProductShop.objects.filter(
            colorproduct__product=product, quantity__gt=0
        )
        .exclude(shop__name__icontains="Склад")
        .select_related("shop", "colorproduct", "colorproduct__color")
    ):
        grouped_data[colorproductshop.colorproduct].append(
            {
                "shop": colorproductshop.shop,
                "quantity": colorproductshop.quantity,
            }
        )

    shops_data = [
        {"colorproduct": color, "items": items}
        for color, items in grouped_data.items()
    ]

    # Добавляем в контекст данные о товаре в интернет магазине
    storage_data = (
        ColorProduct.objects.filter(
            product=product,
            colorproductshop__shop__name__icontains="Склад",
            colorproductshop__quantity__gt=0,
        )
        .select_related("color")
        .annotate(total=Sum("colorproductshop__quantity"))
    )

    # Добавляем список доступных цветов
    available_colors = list(set(
        list(storage_data)
        + [item["colorproduct"] for item in shops_data]
    ))

    # Добавляем выбранные пользователем цвета
    selected_colorproduct = request.GET.getlist("color")

    # Получаем все комментарии и их авторов
    reviews = product.reviews.select_related("user")

    # Проверяем, хочет ли пользователь отредактировать свой отзыв
    if review_id is not None:
        review_instance = get_object_or_404(Review, pk=review_id)
    else:
        review_instance = None

    # Создаем объект формы со всеми данными
    form = ReviewForm(
        request.POST or None,
        files=request.FILES or None,
        instance=review_instance,
    )
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.save()
        return redirect(product.get_absolute_url())

    # Сохраняем все полученные данные в контекст
    context = {
        "product": product,
        "shops_data": shops_data,
        "storage_data": storage_data,
        "available_colors": available_colors,
        "selected_colorproduct": selected_colorproduct,
        "form": form,
        "reviews": reviews,
    }
    return render(request, "main/product_detail.html", context)


def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    form = ReviewForm(request.POST, files=request.FILES or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.product = product
        review.save()
    return redirect(product.get_absolute_url())


def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user == request.user:
        review.delete()
    return redirect(review.product.get_absolute_url())


class CategoryListView(ObjectListViewMixin):
    related_model = Category
    slug_url_kwarg = "category_slug"


class ManufacturerListView(ObjectListViewMixin):
    related_model = Manufacturer
    slug_url_kwarg = "manufacturer_slug"
