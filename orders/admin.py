from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'order_date', 'city', 'category', 'product', 'quantity', 'price')
