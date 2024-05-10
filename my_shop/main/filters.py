import django_filters

from main.models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='actual_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='actual_price', lookup_expr='lte')
    product_name = django_filters.CharFilter(field_name='name')
    shop_id = django_filters.NumberFilter(field_name='shop')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'product_name', 'shop_id']
