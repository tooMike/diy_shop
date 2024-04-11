from django.contrib import admin

from main.models import *


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'sale', 'rating', 'category', 'manufacturer')
    search_fields = ('name',)
    list_filter = ('category', 'manufacturer')


class ProductItemAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'product', 'shop')
    list_filter = ('shop',)


class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name',)
    list_filter = ('country',)


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductItem, ProductItemAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Country)
admin.site.register(Colour)
admin.site.register(Shop)
admin.site.register(Category)
