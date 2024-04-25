from rest_framework import serializers

from main.models import Category, Manufacturer, Product


class ProductSerializer(serializers.ModelSerializer):
    price_with_sale = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name',
    )
    manufacturer = serializers.SlugRelatedField(
        queryset=Manufacturer.objects.all(),
        slug_field='name',
    )

    class Meta:
        model = Product
        fields = ('name', 'category', 'manufacturer', 'rating', 'price', 'sale', 'price_with_sale')

    def price_with_sale(self, obj):
        return obj.price_with_sale

