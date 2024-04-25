from django.shortcuts import render
from rest_framework import mixins, viewsets

from api.serializers import ProductSerializer
from main.models import Product


class RetrieveListViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    pass


class ProductViewSet(RetrieveListViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category')
        manufacturer = self.request.query_params.get('manufacturer')

        if category:
            return queryset.filter(category__slug=category)
        elif manufacturer:
            return queryset.filter(manufacturer__slug=manufacturer)
        return queryset
