from django.conf import settings
from django.db.models import Count, Sum
from django.db.models.base import Model as Model
from django.views.generic import DetailView, ListView

from main.models import Category,Product, Manufacturer
from main.views_mixins import ObjectListViewMixin


paginate_by = getattr(settings, 'PAGINATE_BY', 10)


class ProductListView(ListView):
    """Отображение списка товаров"""
    model = Product
    queryset = Product.objects.select_related(
            'category',
            'manufacturer',
        ).order_by(
            '-rating'
        ).annotate(
            num_shop=Count('shop', distinct=True),
            num_coloursets=Count('colourset', distinct=True),
            num_products=Sum('shopproduct__shopproductcoloursetproduct__quantity', distinct=True),
        )
    paginate_by = paginate_by


class ProductDetailView(DetailView):
    model = Product
    pk_url_kwarg = 'product_id'
    template_name = 'main/product_detail.html'

    def get_queryset(self):


        queryset = self.model.objects.filter(is_active=True).select_related(
            'manufacturer',
            'manufacturer__country',
            'category',
        ).prefetch_related(
            'colourset',
            'colourset__colours',
            'shopproduct_set',
            'shopproduct_set__shopproductcoloursetproduct_set',
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['product']

        shops_data = [{
            'shop': shop_product.shop,
            'items': [{
                    'colourset': colourset_product.coloursetproduct.colourset,
                    'quantity': colourset_product.quantity
            } for colourset_product in shop_product.shopproductcoloursetproduct_set.all()]
        } for shop_product in product.shopproduct_set.all()]
        context['shops_data'] = shops_data
        return context


class CategoryListView(ObjectListViewMixin):
    model = Category
    slug_url_kwarg = 'category_slug'


class ManufacturerListView(ObjectListViewMixin):
    model = Manufacturer
    slug_url_kwarg = 'manufacturer_slug'
