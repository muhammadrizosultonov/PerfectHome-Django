from django.contrib import admin
from .models import OrderRequest


@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "product", "created_at")
    list_filter = ("created_at", "product")
    search_fields = ("name", "phone", "message", "product__name")
    readonly_fields = ("created_at",)
