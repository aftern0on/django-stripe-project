from django.contrib import admin
from .models import Item, Order, Discount, Tax


class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'price', 'currency')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'total_price')
    readonly_fields = ('total_price',)


class DiscountAdmin(admin.ModelAdmin):
    readonly_fields = ('coupon_id',)
    list_display = ('id', 'name', 'percentage')


class TaxAdmin(admin.ModelAdmin):
    readonly_fields = ('rate_id',)
    list_display = ('id', 'name', 'percentage')


admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Tax, TaxAdmin)
