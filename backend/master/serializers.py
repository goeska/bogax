from django.db.models import Q
from rest_framework import serializers

from .models import Coa, LegalEntityType, MainConfig, Product, ProductCategory, TableNumber, Tax, Uom

PRODUCT_DUPLICATE_NAME_ERROR = (
    "That name's already taken - pick another one (upper/lower doesn't matter)."
)

UOM_DUPLICATE_NAME_ERROR = (
    "That UOM name's already taken - pick another (upper/lower doesn't matter)."
)

TAX_DUPLICATE_NAME_ERROR = (
    "That tax name's already taken - pick another (upper/lower doesn't matter)."
)

_PRODUCT_CATEGORY_ID_ERRORS = {
    "null": "Oops, pick a category first.",
    "required": "Oops, pick a category first.",
    "does_not_exist": "That category isn't available.",
    "incorrect_type": "Use a valid category id.",
}

_UOM_ID_ERRORS = {
    "null": "Oops, pick a unit first.",
    "required": "Oops, pick a unit first.",
    "does_not_exist": "That UOM isn't available.",
    "incorrect_type": "Use a valid UOM id.",
}


def _normalized_name(value):
    return (value or "").strip().lower()


def _validate_name_norm_unique(*, model, attrs, instance, error_message):
    name = attrs.get("name", instance.name if instance is not None else "")
    nn = _normalized_name(name)
    if not nn:
        return
    qs = model.objects.filter(name_norm=nn)
    if instance is not None:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise serializers.ValidationError({"name": error_message})


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
                "Send at least one of: is_restaurant, is_customer_maintained."
            )
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    """Foreign keys are exposed as *_id in JSON; ORM uses ``product_category`` / ``uom``."""

    product_category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.filter(is_active=True),
        source="product_category",
        error_messages=_PRODUCT_CATEGORY_ID_ERRORS,
    )
    uom_id = serializers.PrimaryKeyRelatedField(
        queryset=Uom.objects.filter(is_active=True),
        source="uom",
        error_messages=_UOM_ID_ERRORS,
    )
    uom_name = serializers.CharField(source="uom.name", read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = getattr(self, "instance", None)
        cat_qs = ProductCategory.objects.filter(is_active=True)
        if inst is not None and getattr(inst, "product_category_id", None) is not None:
            cat_qs = ProductCategory.objects.filter(
                Q(is_active=True) | Q(pk=inst.product_category_id)
            )
        self.fields["product_category_id"].queryset = cat_qs
        uom_qs = Uom.objects.filter(is_active=True)
        if inst is not None and getattr(inst, "uom_id", None) is not None:
            uom_qs = Uom.objects.filter(Q(is_active=True) | Q(pk=inst.uom_id))
        self.fields["uom_id"].queryset = uom_qs

    def validate(self, attrs):
        _validate_name_norm_unique(
            model=Product,
            attrs=attrs,
            instance=getattr(self, "instance", None),
            error_message=PRODUCT_DUPLICATE_NAME_ERROR,
        )
        return attrs

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
    def validate(self, attrs):
        _validate_name_norm_unique(
            model=ProductCategory,
            attrs=attrs,
            instance=getattr(self, "instance", None),
            error_message=(
                "That category name's already taken - try another "
                "(upper/lower doesn't matter)."
            ),
        )
        return attrs

    class Meta:
        model = ProductCategory
        fields = ("id", "name", "is_active")


class TableNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableNumber
        fields = ("id", "name", "is_active")


class TaxSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        _validate_name_norm_unique(
            model=Tax,
            attrs=attrs,
            instance=getattr(self, "instance", None),
            error_message=TAX_DUPLICATE_NAME_ERROR,
        )
        return attrs

    class Meta:
        model = Tax
        fields = ("id", "name", "rate_percent", "is_active")


class UomSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        _validate_name_norm_unique(
            model=Uom,
            attrs=attrs,
            instance=getattr(self, "instance", None),
            error_message=UOM_DUPLICATE_NAME_ERROR,
        )
        return attrs

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
            raise serializers.ValidationError({"parent_id": "A row can't be its own parent."})
        if parent is not None and parent.parent_id is not None:
            raise serializers.ValidationError(
                {"parent_id": "Only two levels deep - pick a top-level account as parent."}
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
