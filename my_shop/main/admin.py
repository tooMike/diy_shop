import nested_admin
from django.contrib import admin

from main.models import (Category, Colour, ColourProduct, Country,
                         Manufacturer, Product, Shop,
                         ColourProductShop)



class ColourProductShopInline(nested_admin.NestedStackedInline):
    model = ColourProductShop
    extra = 0


class ColourProductInline(nested_admin.NestedStackedInline):
    model = ColourProduct
    extra = 0
    inlines = (ColourProductShopInline,)


class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = (
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
    inlines = (ColourProductInline,)


class ManufacturerAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)
    list_filter = ("country",)


admin.site.register(Product, ProductAdmin)
admin.site.register(Colour)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Country)
admin.site.register(Shop)
admin.site.register(Category)
