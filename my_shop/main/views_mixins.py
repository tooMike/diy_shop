from django.conf import settings
from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404
from django_filters.views import FilterView

from main.filters import ProductFilter
from main.models import Category, Manufacturer, Product, Shop

paginate_by = getattr(settings, "PAGINATE_BY", 10)


class BaseObjectListViewMixin(FilterView):

    template_name = "main/product_list.html"
    model = Product
    paginate_by = paginate_by
    filterset_class = ProductFilter

    def get_queryset(self):
        """Получаем все товары"""
        queryset = (
            Product.objects.filter(is_active=True)
            .select_related(
                "manufacturer",
                "category",
            )
            .annotate(
                num_shop=Count("shop", distinct=True),
                num_products=Sum(
                    "shopproduct__shopproductcolourproduct__quantity",
                    distinct=True,
                ),
                rating=Avg("reviews__rating"),
            )
            .order_by("-rating")
        )

        # Обработка сортировки (по цене и по рейтингу)
        product_sort = self.request.GET.get("product_sort")
        if product_sort:
            queryset = queryset.order_by(product_sort)

        # # Полнотекстовый поиск
        # product_name = self.request.GET.get('product_name')
        # if product_name:
        #     queryset = queryset.filter(name__search=product_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shops"] = Shop.objects.all()

        # Передаем в контекст все shop_id из url (для фильтра по магазинам)
        context["selected_shop_ids"] = self.request.GET.getlist("shop_id")
        return context


class ObjectListViewMixin(BaseObjectListViewMixin):
    """
    Отображение списка товаров связанных с указанной моделью.
    Переопределять в наследуемых классах нужно: slug_url_kwarg и related_model.
    """

    slug_url_kwarg = Category
    related_model = "category_slug"

    def get_related_object(self):
        """Получаем нужный связанный объект."""
        related_object = get_object_or_404(
            self.related_model,
            slug=self.kwargs[self.slug_url_kwarg],
            is_active=True,
        )
        return related_object

    def get_queryset(self):
        """Получаем все товары связанные с указанной моделью"""
        queryset = super().get_queryset()
        if self.related_model is not None:
            related_object = self.get_related_object()
            if self.related_model == Category:
                queryset = queryset.filter(category=related_object.id)
            if self.related_model == Manufacturer:
                queryset = queryset.filter(manufacturer=related_object.id)
        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем сам связанный объект в словарь контекста"""
        context = super().get_context_data(**kwargs)
        related_object = self.get_related_object()
        context["related_object"] = related_object
        context["h1"] = related_object.name
        return context
