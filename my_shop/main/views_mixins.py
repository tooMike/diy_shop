from django.conf import settings
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from main.models import Category

paginate_by = getattr(settings, 'PAGINATE_BY', 10)


class ObjectListViewMixin(ListView):
    """Отображения списка товаров с заданным параметром."""

    slug_url_kwarg = 'category_slug'
    template_name = 'main/product_list.html'
    model = Category
    paginate_by = paginate_by

    def get_category(self):
        """Получаем нужную категорию."""
        category = get_object_or_404(
            self.model,
            slug=self.kwargs[self.slug_url_kwarg],
            is_active=True
        )
        return category

    def get_queryset(self):
        """Получаем все товары в нужной категории"""
        category = self.get_category()
        return category.product.filter(is_active=True).annotate(rating=Avg('reviews__rating')).order_by('-rating')

    def get_context_data(self, **kwargs):
        """Добавляем саму категорию в словарь контекста"""
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        context['category'] = category
        context['h1'] = category.name
        return context
