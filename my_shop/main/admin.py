import nested_admin
from django.contrib import admin

from main.models import (Category, Color, ColorProduct, Country,
                         Manufacturer, Product, Shop,
                         ColorProductShop)



class ColorProductShopInline(nested_admin.NestedStackedInline):
    model = ColorProductShop
    extra = 0


class ColorProductInline(nested_admin.NestedStackedInline):
    model = ColorProduct
    extra = 0
    inlines = (ColorProductShopInline,)


class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "sale",
        "average_rating",
        "category",
        "manufacturer",
    )
    search_fields = ("name",)
    list_filter = ("category", "manufacturer")
    readonly_fields = ("actual_price", "average_rating")
    fields = (
        "name",
        "description",
        "category",
        "manufacturer",
        "price",
        "sale",
        "actual_price",
        "is_active",
        "image",
        "average_rating",
    )
    inlines = (ColorProductInline,)


class ManufacturerAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)
    list_filter = ("country",)


admin.site.register(Product, ProductAdmin)
admin.site.register(Color)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Country)
admin.site.register(Shop)
admin.site.register(Category)
