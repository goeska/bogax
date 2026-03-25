from django.conf import settings
from django.db import models

from master.models import Product, Tax
from sales.models import Partner


class PurchaseOrder(models.Model):
    class State(models.TextChoices):
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        RECEIVED = "received", "Received"
        VOID = "void", "Void"

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="purchase_orders",
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT,
        related_name="purchase_orders",
    )
    time_transaction = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    state = models.CharField(
        max_length=20,
        choices=State.choices,
        default=State.DRAFT,
        db_index=True,
    )
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "purchase_order"
        ordering = ["-time_transaction", "-id"]
        indexes = [
            models.Index(fields=["-update_at"], name="idx_po_update_at"),
            models.Index(fields=["state", "-update_at"], name="idx_po_state_update_at"),
            models.Index(fields=["created_by"], name="idx_po_created_by"),
        ]


class PurchaseOrderLine(models.Model):
    id = models.AutoField(primary_key=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="purchase_order_lines",
    )
    quantity = models.DecimalField(max_digits=20, decimal_places=2)
    unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    is_active = models.BooleanField(default=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "purchase_order_line"
        indexes = [
            models.Index(fields=["purchase_order", "id"], name="idx_pol_order_id"),
        ]


class PurchaseOrderLineTax(models.Model):
    id = models.AutoField(primary_key=True)
    purchase_order_line = models.ForeignKey(
        PurchaseOrderLine,
        on_delete=models.CASCADE,
        related_name="line_taxes",
    )
    tax = models.ForeignKey(
        Tax,
        on_delete=models.PROTECT,
        related_name="purchase_order_line_taxes",
    )
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "purchase_order_line_tax"
        constraints = [
            models.UniqueConstraint(
                fields=["purchase_order_line", "tax"],
                name="purchase_order_line_tax_purchase_order_line_id_tax_id_key",
            ),
        ]


class ReceivingOrder(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    purchase_order_line = models.ForeignKey(
        PurchaseOrderLine,
        on_delete=models.PROTECT,
        related_name="receiving_orders",
    )
    quantity_received = models.DecimalField(max_digits=20, decimal_places=2)
    received_date = models.DateTimeField()
    state = models.CharField(max_length=20, default="draft")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(null=True, blank=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "receiving_order"
        managed = False
        ordering = ["-received_date", "-id"]
