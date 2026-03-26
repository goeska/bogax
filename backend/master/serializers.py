from rest_framework import serializers

from .models import Coa, LegalEntityType, MainConfig, Product, ProductCategory, TableNumber, Tax, Uom


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
            "product_type",
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


class CoaSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Coa.objects.all(),
        source="parent",
        allow_null=True,
        required=False,
    )
    parent_code = serializers.CharField(source="parent.code", read_only=True)
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    def validate(self, attrs):
        parent = attrs.get("parent")
        instance = getattr(self, "instance", None)
        if instance is not None and parent is not None and parent.pk == instance.pk:
            raise serializers.ValidationError({"parent_id": "Parent cannot be self."})
        if parent is not None and parent.parent_id is not None:
            raise serializers.ValidationError(
                {"parent_id": "Only 2 levels allowed. Parent must be a top-level CoA."}
            )
        return attrs

    class Meta:
        model = Coa
        fields = (
            "id",
            "code",
            "name",
            "parent_id",
            "parent_code",
            "parent_name",
            "is_active",
        )


class LegalEntityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalEntityType
        fields = ("id", "code", "name", "is_active")
