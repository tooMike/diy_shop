from django.contrib import admin

from orders.models import Order, OrderProduct

admin.site.register(Order)
admin.site.register(OrderProduct)
