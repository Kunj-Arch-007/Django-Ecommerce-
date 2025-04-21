from django.contrib import admin
from .models import Customer, Product, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'order_date', 'address']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number']
    search_fields = ['order_number', 'customer__name']
    list_filter = ['order_date']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_number', 'email']
    search_fields = ['name', 'email']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'weight']
    search_fields = ['name']
