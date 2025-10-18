from django.contrib import admin
from .models import Order, Payment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id","product_code","user_id","amount","status","created_at")
    list_filter = ("status",)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id","order","amount","approved","created_at")
    list_filter = ("approved",)
