from django.contrib import admin
from .models import Order,Payment,OrderProduct
# Register your models here.

class OrderProductInline(admin.TabularInline) :
    model=OrderProduct
    extra=0

class OrderAdmin(admin.ModelAdmin) :
    list_display=['order_number','full_name','created_at']
    list_filter=['status','is_ordered']
    search_fields=['order_number','first_name','last_name']
    list_per_page=40
    inlines=[OrderProductInline]

admin.site.register(Order,OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)

