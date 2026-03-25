from django.contrib import admin

from .models import Product, ProductCategory, TableNumber, Tax, Uom


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "product_category",
        "uom",
        "is_active",
        "unit_price",
    )
    list_filter = ("is_active", "product_category", "uom")
    search_fields = ("name",)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(TableNumber)
class TableNumberAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    list_filter = ("is_active",)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rate_percent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Uom)
class UomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
