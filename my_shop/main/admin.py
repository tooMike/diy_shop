from django.contrib import admin
import nested_admin

from main.models import *


class ShopProductColourSetInline(nested_admin.NestedStackedInline):
    model = ShopProductColourProduct
    extra = 0


class ShopProductInline(nested_admin.NestedStackedInline):
    model = ShopProduct
    extra = 0
    inlines = (ShopProductColourSetInline,)


class ColourProductInline(nested_admin.NestedStackedInline):
    model = ColourProduct
    extra = 0


class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'price', 'sale', 'average_rating', 'category', 'manufacturer')
    search_fields = ('name',)
    list_filter = ('category', 'manufacturer')
    inlines = (ShopProductInline, ColourProductInline)


class ManufacturerAdmin(nested_admin.NestedModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name',)
    list_filter = ('country',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Colour)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Country)
admin.site.register(Shop)
admin.site.register(Category)
