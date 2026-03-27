from decimal import Decimal

from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist

from master.models import Product

from master.models import LegalEntityType

from .models import Partner, Project, SalesOrder, SalesOrderLine, SalesOrderLineTax


class PartnerMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ("id", "name", "phone")


class PartnerSerializer(serializers.ModelSerializer):
    legal_entity_type_id = serializers.PrimaryKeyRelatedField(
        queryset=LegalEntityType.objects.all(),
        source="legal_entity_type",
        allow_null=True,
        required=False,
    )
    legal_entity_type_code = serializers.CharField(source="legal_entity_type.code", read_only=True)
    legal_entity_type_name = serializers.CharField(source="legal_entity_type.name", read_only=True)

    def validate(self, attrs):
        let = attrs.get("legal_entity_type")
        if let is not None:
            attrs["is_corporate"] = True
        return attrs

    class Meta:
        model = Partner
        fields = (
            "id",
            "name",
            "phone",
            "address",
            "legal_entity_type_id",
            "legal_entity_type_code",
            "legal_entity_type_name",
            "is_corporate",
            "is_customer",
            "is_vendor",
            "is_active",
        )
        read_only_fields = ("id",)


class SalesOrderLineTaxReadSerializer(serializers.ModelSerializer):
    tax_name = serializers.CharField(source="tax.name", read_only=True)
    rate_percent = serializers.DecimalField(
        source="tax.rate_percent",
        max_digits=20,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = SalesOrderLineTax
        fields = ("id", "tax_id", "tax_name", "rate_percent")


class SalesOrderLineReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_category_id = serializers.IntegerField(
        source="product.product_category_id",
        read_only=True,
    )
    line_taxes = SalesOrderLineTaxReadSerializer(many=True, read_only=True)

    class Meta:
        model = SalesOrderLine
        fields = (
            "id",
            "product_id",
            "product_category_id",
            "product_name",
            "quantity",
            "unit_price",
            "line_taxes",
        )


class SalesOrderLineListSerializer(serializers.ModelSerializer):
    sales_order_id = serializers.IntegerField(source="sales_order.id", read_only=True)
    sales_order_code = serializers.CharField(source="sales_order.code", read_only=True)
    transaction_at = serializers.DateTimeField(source="sales_order.time_transaction", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_taxes = SalesOrderLineTaxReadSerializer(many=True, read_only=True)
    tax_total = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    def _line_subtotal(self, obj):
        return round(float(obj.quantity) * float(obj.unit_price))

    def get_tax_total(self, obj):
        subtotal = self._line_subtotal(obj)
        total = 0
        for lt in obj.line_taxes.all():
            r = float(lt.tax.rate_percent)
            total += round(subtotal * (r / 100.0))
        return total

    def get_line_total(self, obj):
        return self._line_subtotal(obj) + self.get_tax_total(obj)

    class Meta:
        model = SalesOrderLine
        fields = (
            "id",
            "sales_order_id",
            "sales_order_code",
            "transaction_at",
            "product_id",
            "product_name",
            "quantity",
            "unit_price",
            "line_taxes",
            "tax_total",
            "line_total",
        )


def _sales_order_amounts(order):
    """Subtotal (lines), tax sum, grand total — mirrors POS line math (integer IDR)."""
    sub_total = 0
    tax_total = 0
    for line in order.lines.filter(is_active=True):
        try:
            qty = float(line.quantity or 0)
        except (TypeError, ValueError):
            qty = 0.0
        try:
            price = float(line.unit_price or 0)
        except (TypeError, ValueError):
            price = 0.0
        sub = round(qty * price)
        sub_total += sub
        for lt in line.line_taxes.all():
            try:
                if not lt.tax_id:
                    continue
                r = float(lt.tax.rate_percent or 0)
            except ObjectDoesNotExist:
                continue
            except (TypeError, ValueError, AttributeError):
                continue
            tax_total += round(sub * (r / 100.0))
    return sub_total, tax_total, sub_total + tax_total


class SalesOrderReadSerializer(serializers.ModelSerializer):
    customer = PartnerMiniSerializer(source="partner", read_only=True)
    partner = PartnerMiniSerializer(read_only=True)
    table_id = serializers.IntegerField(source="table_number_id", read_only=True, allow_null=True)
    table_name = serializers.SerializerMethodField()
    project_id = serializers.IntegerField(read_only=True, allow_null=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    created_at = serializers.DateTimeField(source="update_at", read_only=True)
    updated_at = serializers.DateTimeField(source="update_at", read_only=True)
    subtotal = serializers.IntegerField(read_only=True)
    tax_total = serializers.IntegerField(read_only=True)
    grand_total = serializers.IntegerField(read_only=True)
    order_type = serializers.CharField(read_only=True)

    def get_table_name(self, obj):
        if obj.table_number_id is None:
            return None
        return obj.table_number.name

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        s, t, g = _sales_order_amounts(instance)
        ret["subtotal"] = s
        ret["tax_total"] = t
        ret["grand_total"] = g
        return ret

    lines = serializers.SerializerMethodField()

    def get_lines(self, obj):
        qs = obj.lines.filter(is_active=True).prefetch_related("line_taxes__tax")
        return SalesOrderLineReadSerializer(qs, many=True).data

    class Meta:
        model = SalesOrder
        fields = (
            "id",
            "code",
            "created_by_id",
            "state",
            "order_type",
            "time_transaction",
            "created_at",
            "updated_at",
            "subtotal",
            "tax_total",
            "grand_total",
            "customer",
            "partner",
            "table_id",
            "table_name",
            "project_id",
            "project_name",
            "lines",
        )


class PosSaveDraftSerializer(serializers.Serializer):
    ORDER_TYPE_CHOICES = ("retail", "non_retail")

    transaction_at = serializers.DateTimeField()
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=Decimal("0.01"))
    unit_price = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=Decimal("0"))
    apply_ppn = serializers.BooleanField(default=False)
    ppn_tax_id = serializers.IntegerField(required=False, allow_null=True)
    tax_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
    )
    table = serializers.CharField(required=False, allow_blank=True, max_length=50)
    customer_name = serializers.CharField(required=False, allow_blank=True, max_length=100)
    customer_phone = serializers.CharField(required=False, allow_blank=True, max_length=50)
    partner_name = serializers.CharField(required=False, allow_blank=True, max_length=100)
    partner_phone = serializers.CharField(required=False, allow_blank=True, max_length=50)
    partner_id = serializers.IntegerField(required=False, allow_null=True)
    project_id = serializers.IntegerField(required=False, allow_null=True)
    order_type = serializers.ChoiceField(choices=ORDER_TYPE_CHOICES, required=False)
    sales_order_id = serializers.IntegerField(required=False, allow_null=True)
    sales_order_line_id = serializers.IntegerField(required=False, allow_null=True)
    append_line = serializers.BooleanField(default=False)

    def validate(self, attrs):
        # Keep backward compatibility: if partner_* is provided, map it to customer_*.
        if "partner_name" in attrs:
            attrs["customer_name"] = attrs.get("partner_name", "")
        if "partner_phone" in attrs:
            attrs["customer_phone"] = attrs.get("partner_phone", "")
        if attrs.get("apply_ppn"):
            tax_ids = attrs.get("tax_ids") or []
            if not tax_ids and not attrs.get("ppn_tax_id"):
                raise serializers.ValidationError(
                    {"tax_ids": "Select at least one tax when tax is applied."}
                )
        order_type = attrs.get("order_type") or "retail"
        if order_type == "non_retail":
            if not attrs.get("partner_id"):
                raise serializers.ValidationError(
                    {"partner_id": "Required when order_type is non_retail."}
                )
            if not attrs.get("project_id"):
                raise serializers.ValidationError(
                    {"project_id": "Required when order_type is non_retail."}
                )
        return attrs

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive product.")
        return value


class ProjectSerializer(serializers.ModelSerializer):
    partner_id = serializers.PrimaryKeyRelatedField(
        queryset=Partner.objects.all(),
        source="partner",
    )
    partner_name = serializers.CharField(source="partner.name", read_only=True)

    class Meta:
        model = Project
        fields = ("id", "code", "name", "partner_id", "partner_name", "is_active", "update_at")
        read_only_fields = ("id", "code", "update_at")
