from django.contrib import admin
from .models import Product, ProductImage, ProductTag


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "price", "country_of_origin")
    list_filter = ("brand", "category", "country_of_origin", "tags")
    search_fields = ("name", "article_number", "description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("brand", "category")
    filter_horizontal = ("tags",)
    inlines = [ProductImageInline]


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    list_filter = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "alt_text")
    search_fields = ("product__name",)
