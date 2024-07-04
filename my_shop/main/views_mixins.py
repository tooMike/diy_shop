from django.conf import settings
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
    SearchRank,
)
from django.db.models import Avg, Count, OuterRef, Subquery, Sum
from django.shortcuts import get_object_or_404
from django_filters.views import FilterView

from main.filters import ProductFilter
from main.models import Category, ColorProductShop, Manufacturer, Product, Shop

paginate_by = getattr(settings, "PAGINATE_BY", 10)


class BaseObjectListViewMixin(FilterView):

    template_name = "main/product_list.html"
    model = Product
    paginate_by = paginate_by
    filterset_class = ProductFilter

    def get_queryset(self):
        """Получаем все товары"""
        queryset = (
            Product.objects.filter(
                is_active=True,
                # отдает только товары, которые есть в магазинах
                colorproduct__colorproductshop__quantity__gt=0,
            )
            .select_related(
                "manufacturer",
                "category",
            )
            .annotate(
                # Добавляем количество магазинов, где есть товар
                num_shop=Count(
                    "colorproduct__colorproductshop__shop", distinct=True
                ),
                # Добавляем доступное количество товаров
                num_products=Subquery(
                    ColorProductShop.objects.filter(
                        colorproduct__product=OuterRef("pk")
                    )
                    .values("colorproduct__product")
                    .annotate(total=Sum("quantity"))
                    .values("total")
                ),
                rating=Avg("reviews__rating"),
            )
            .order_by("-rating")
        )

        # Обработка сортировки (по цене и по рейтингу)
        product_sort = self.request.GET.get("product_sort")
        if product_sort:
            queryset = queryset.order_by(product_sort)

        # Полнотекстовый поиск: только для PostgreSQL
        product_name = self.request.GET.get("product_name")
        if product_name:
            search_query = SearchQuery(product_name)
            queryset = queryset.annotate(
                search=SearchVector("name", "description"),
            ).filter(search=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shops"] = Shop.objects.exclude(name__icontains="Склад")
        # Передаем в контекст все shop_id из url (для фильтра по магазинам)
        context["selected_shop_ids"] = self.request.GET.getlist("shop_id")

        return context


class ObjectListViewMixin(BaseObjectListViewMixin):
    """
    Отображение списка товаров связанных с указанной моделью.
    Переопределять в наследуемых классах нужно: slug_url_kwarg и related_model.
    """

    slug_url_kwarg = "category_slug"
    related_model = Category

    def get_related_object(self):
        """Получаем нужный связанный объект."""
        related_object = get_object_or_404(
            self.related_model,
            slug=self.kwargs.get(self.slug_url_kwarg),
            is_active=True,
        )
        return related_object

    def get_queryset(self):
        """Получаем все товары связанные с указанной моделью"""
        queryset = super().get_queryset()
        if self.related_model is not None:
            if self.related_model == Category:
                queryset = queryset.filter(
                    category__slug=self.kwargs.get(self.slug_url_kwarg)
                )
            if self.related_model == Manufacturer:
                queryset = queryset.filter(
                    manufacturer__slug=self.kwargs.get(self.slug_url_kwarg)
                )
        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем сам связанный объект в словарь контекста"""
        context = super().get_context_data(**kwargs)
        related_object = self.get_related_object()
        context["related_object"] = related_object
        context["h1"] = related_object.name
        return context
