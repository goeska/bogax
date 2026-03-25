from decimal import Decimal

from rest_framework import serializers

from master.models import Product
from sales.serializers import PartnerMiniSerializer

from .models import PurchaseOrder, PurchaseOrderLine, PurchaseOrderLineTax, ReceivingOrder


class PurchaseOrderLineTaxReadSerializer(serializers.ModelSerializer):
    tax_name = serializers.CharField(source="tax.name", read_only=True)
    rate_percent = serializers.DecimalField(
        source="tax.rate_percent",
        max_digits=20,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = PurchaseOrderLineTax
        fields = ("id", "tax_id", "tax_name", "rate_percent")


class PurchaseOrderLineReadSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_category_id = serializers.IntegerField(
        source="product.product_category_id",
        read_only=True,
    )
    line_taxes = PurchaseOrderLineTaxReadSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrderLine
        fields = (
            "id",
            "product_id",
            "product_category_id",
            "product_name",
            "quantity",
            "unit_price",
            "line_taxes",
        )


def _purchase_order_amounts(order):
    sub_total = 0
    tax_total = 0
    for line in order.lines.filter(is_active=True):
        sub = round(float(line.quantity) * float(line.unit_price))
        sub_total += sub
        for lt in line.line_taxes.all():
            r = float(lt.tax.rate_percent)
            tax_total += round(sub * (r / 100.0))
    return sub_total, tax_total, sub_total + tax_total


class PurchaseOrderReadSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source="update_at", read_only=True)
    updated_at = serializers.DateTimeField(source="update_at", read_only=True)
    subtotal = serializers.IntegerField(read_only=True)
    tax_total = serializers.IntegerField(read_only=True)
    grand_total = serializers.IntegerField(read_only=True)
    partner = PartnerMiniSerializer(read_only=True)
    vendor_name = serializers.CharField(source="partner.name", read_only=True)
    vendor_phone = serializers.CharField(source="partner.phone", read_only=True)
    partner_id = serializers.IntegerField(read_only=True)
    lines = serializers.SerializerMethodField()

    def get_lines(self, obj):
        qs = obj.lines.filter(is_active=True).prefetch_related("line_taxes__tax")
        return PurchaseOrderLineReadSerializer(qs, many=True).data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        s, t, g = _purchase_order_amounts(instance)
        ret["subtotal"] = s
        ret["tax_total"] = t
        ret["grand_total"] = g
        return ret

    class Meta:
        model = PurchaseOrder
        fields = (
            "id",
            "code",
            "created_by_id",
            "state",
            "time_transaction",
            "created_at",
            "updated_at",
            "subtotal",
            "tax_total",
            "grand_total",
            "partner_id",
            "partner",
            "vendor_name",
            "vendor_phone",
            "lines",
        )


class PurchaseSaveDraftSerializer(serializers.Serializer):
    transaction_at = serializers.DateTimeField()
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=Decimal("0.01"))
    unit_price = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=Decimal("0"))
    tax_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
        default=list,
    )
    vendor_name = serializers.CharField(required=False, allow_blank=True, max_length=100)
    vendor_phone = serializers.CharField(required=False, allow_blank=True, max_length=50)
    purchase_order_id = serializers.IntegerField(required=False, allow_null=True)
    purchase_order_line_id = serializers.IntegerField(required=False, allow_null=True)
    append_line = serializers.BooleanField(default=False)

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive product.")
        return value


class ReceivingOrderReadSerializer(serializers.ModelSerializer):
    purchase_order_id = serializers.IntegerField(source="purchase_order_line.purchase_order_id", read_only=True)
    purchase_order_code = serializers.CharField(source="purchase_order_line.purchase_order.code", read_only=True)
    purchase_order_line_id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(source="purchase_order_line.product_id", read_only=True)
    product_name = serializers.CharField(source="purchase_order_line.product.name", read_only=True)
    vendor_name = serializers.CharField(source="purchase_order_line.purchase_order.partner.name", read_only=True)
    vendor_phone = serializers.CharField(source="purchase_order_line.purchase_order.partner.phone", read_only=True)

    class Meta:
        model = ReceivingOrder
        fields = (
            "id",
            "code",
            "purchase_order_id",
            "purchase_order_code",
            "purchase_order_line_id",
            "product_id",
            "product_name",
            "vendor_name",
            "vendor_phone",
            "quantity_received",
            "received_date",
            "state",
            "notes",
            "is_active",
            "update_at",
        )


class ReceivingOrderCreateSerializer(serializers.Serializer):
    purchase_order_line_id = serializers.IntegerField(min_value=1)
    quantity_received = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=Decimal("0.01"))
    received_date = serializers.DateTimeField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ReceivingOrderUpdateSerializer(serializers.Serializer):
    purchase_order_line_id = serializers.IntegerField(min_value=1, required=False)
    quantity_received = serializers.DecimalField(
        max_digits=20,
        decimal_places=2,
        min_value=Decimal("0.01"),
        required=False,
    )
    received_date = serializers.DateTimeField(required=False)


class PurchaseOrderLineListSerializer(serializers.ModelSerializer):
    purchase_order_id = serializers.IntegerField(source="purchase_order.id", read_only=True)
    purchase_order_code = serializers.CharField(source="purchase_order.code", read_only=True)
    transaction_at = serializers.DateTimeField(source="purchase_order.time_transaction", read_only=True)
    vendor_name = serializers.CharField(source="purchase_order.partner.name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    ordered_quantity = serializers.DecimalField(source="quantity", max_digits=20, decimal_places=2, read_only=True)
    received_quantity = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    outstanding_quantity = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrderLine
        fields = (
            "id",
            "purchase_order_id",
            "purchase_order_code",
            "transaction_at",
            "vendor_name",
            "product_id",
            "product_name",
            "ordered_quantity",
            "received_quantity",
            "outstanding_quantity",
            "unit_price",
        )
