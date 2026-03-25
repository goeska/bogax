from rest_framework import serializers

from .models import MainConfig, Product, ProductCategory, TableNumber, Tax, Uom


class MainConfigReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainConfig
        fields = ("id", "is_restaurant", "is_customer_maintained")


class MainConfigUpdateSerializer(serializers.Serializer):
    is_restaurant = serializers.BooleanField(required=False)
    is_customer_maintained = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "Provide at least one of: is_restaurant, is_customer_maintained."
            )
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    """FK ditulis sebagai *_id di JSON; ORM memakai field ``product_category`` / ``uom``."""

    product_category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        source="product_category",
    )
    uom_id = serializers.PrimaryKeyRelatedField(
        queryset=Uom.objects.all(),
        source="uom",
    )
    uom_name = serializers.CharField(source="uom.name", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "product_category_id",
            "uom_id",
            "uom_name",
            "is_active",
            "unit_price",
        )


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ("id", "name", "is_active")


class TableNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableNumber
        fields = ("id", "name", "is_active")


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ("id", "name", "rate_percent", "is_active")


class UomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uom
        fields = ("id", "name", "is_active")
