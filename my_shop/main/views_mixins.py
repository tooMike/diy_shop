from django.conf import settings
from django.db.models import Avg, Count, OuterRef, Subquery, Sum
from django.shortcuts import get_object_or_404
from django_filters.views import FilterView

from main.filters import ProductFilter
from main.models import Category, ColorProductShop, Manufacturer, Product, Shop
from shopping_cart.models import ShoppingCart

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
                # Добавляем количество доступное количество товаров
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

        # # Добавляем в контекст словарь с {id_товара: количество_в_корзине, ...}
        # # текущего пользователя для проверки в шаблоне,
        # # есть ли конкретный товар в корзине пользователя
        # # и отображения количества товара в корзине
        # users_shopping_carts = ShoppingCart.objects.all().select_related(
        #     "product"
        # )
        # # Для авторизированного пользователя фильтруем по user
        # if self.request.user.is_authenticated:
        #     users_shopping_carts = users_shopping_carts.filter(
        #         user=self.request.user
        #     )
        # # Для анонимного пользователя фильтруем по session_key
        # else:
        #     users_shopping_carts = users_shopping_carts.filter(
        #         session_key=self.request.session.session_key
        #     )
        # # Формируем словарь {id_товара: количество_в_корзине, ...}
        # products_in_user_shopping_carts = {}
        # for cart in users_shopping_carts:
        #     products_in_user_shopping_carts[cart.product.id] = cart.quantity
        # context["products_in_user_shopping_carts"] = (
        #     products_in_user_shopping_carts
        # )
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
