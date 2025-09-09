from django.contrib import admin
from .models import Category, Product, ProductVariant, ProductMeasurement, InventoryLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active", "sort_order", "product_count")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("sort_order", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sku", "status", "price", "stock", "is_featured", "is_new", "is_on_sale")
    list_filter = ("status", "is_featured", "is_new", "is_on_sale", "category")
    search_fields = ("name", "sku", "description")
    autocomplete_fields = ("category",)
    ordering = ("-created_at",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "sku", "price", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "sku")
    autocomplete_fields = ("product",)


@admin.register(ProductMeasurement)
class ProductMeasurementAdmin(admin.ModelAdmin):
    list_display = ("product", "measurement", "quantity", "price", "original_price", "is_active", "is_default", "sort_order")
    list_filter = ("is_active", "is_default", "measurement")
    search_fields = ("product__name",)
    autocomplete_fields = ("product",)
    ordering = ("product", "sort_order")


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ("product", "log_type", "quantity", "previous_stock", "new_stock", "created_at")
    list_filter = ("log_type",)
    search_fields = ("product__name",)
    autocomplete_fields = ("product",)
    ordering = ("-created_at",)
