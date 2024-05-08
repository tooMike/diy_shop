from django.conf import settings
from django.db.models import Avg, Count, Sum
from django.db.models.base import Model as Model
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from main.forms import ReviewForm
from main.models import Category, Manufacturer, Product, Review
from main.views_mixins import ObjectListViewMixin

paginate_by = getattr(settings, 'PAGINATE_BY', 10)


class ProductListView(ListView):
    """Отображение списка товаров"""
    model = Product
    queryset = Product.objects.select_related(
            'category',
            'manufacturer',
        ).annotate(
            num_shop=Count('shop', distinct=True),
            num_colours=Count('colour', distinct=True),
            num_products=Sum('shopproduct__shopproductcolourproduct__quantity', distinct=True),
            rating=Avg('reviews__rating'),
        ).order_by(
            '-rating'
        )
    paginate_by = paginate_by


def product_detail_view(request, product_id, review_id=None):
    """Отображение страницы товара"""
    queryset = Product.objects.annotate(rating=Avg('reviews__rating'), reviews_count=Count('reviews'),)
    product = get_object_or_404(queryset, id=product_id, is_active=True)

    # Добавляем в контекст данные о товаре
    shops_data = [{
        'shop': shopproduct.shop,
        'items': [{
            'colour': item.colourproduct,
            'quantity': item.quantity
        } for item in shopproduct.shopproductcolourproduct_set.select_related(
            'colourproduct',
            'colourproduct__colour'
        )]
    } for shopproduct in product.shopproduct_set.select_related('shop')]

    # Получаем все комментарии и их авторов
    reviews = product.reviews.select_related('author')

    # Проверяем, хочет ли пользователь отредактировать свой отзыв
    if review_id is not None:
        review_instance = get_object_or_404(Review, pk=review_id)
    else:
        review_instance = None

    # Создаем объект формы со всеми данными
    form = ReviewForm(request.POST or None, files=request.FILES or None, instance=review_instance)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        review.product = product
        review.save()
        return redirect(product.get_absolute_url())

    # Сохраняем все полученные данные в контекст
    context = {
        'product': product,
        'shops_data': shops_data,
        'form': form,
        'reviews': reviews,
    }
    return render(request, 'main/product_detail.html', context)


def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    form = ReviewForm(request.POST, files=request.FILES or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.author = request.user
        review.product = product
        review.save()
    return redirect(product.get_absolute_url())


def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.author == request.user:
        review.delete()
    return redirect(review.product.get_absolute_url())


class CategoryListView(ObjectListViewMixin):
    model = Category
    slug_url_kwarg = 'category_slug'


class ManufacturerListView(ObjectListViewMixin):
    model = Manufacturer
    slug_url_kwarg = 'manufacturer_slug'
