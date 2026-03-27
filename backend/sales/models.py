"""
Sales tables are Django-managed (``managed = True``).

Schema is applied with ``python manage.py migrate`` — commit migrations and run
migrate on every deploy. Table names stay without ``bx_`` prefix.

**Database already has these tables?** Once, run:
``python manage.py migrate sales --fake-initial``
so Django records the initial migration without recreating tables.
"""
from django.conf import settings
from django.db import models

from master.models import LegalEntityType, Product, TableNumber, Tax


class Partner(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    address = models.CharField(max_length=255, blank=True, default="")
    legal_entity_type = models.ForeignKey(
        LegalEntityType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_column="legal_entity_type_id",
        related_name="partners",
    )
    is_corporate = models.BooleanField(default=False, db_index=True)
    name_norm = models.CharField(max_length=100, editable=False, default="", db_index=True)
    phone_norm = models.CharField(max_length=50, editable=False, default="", db_index=True)
    is_customer = models.BooleanField(default=False, db_index=True)
    is_vendor = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "partner"
        constraints = [
            models.UniqueConstraint(
                fields=["name_norm", "phone_norm"],
                name="unique_partner_name_norm_phone_norm",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.legal_entity_type_id is not None and not self.is_corporate:
            self.is_corporate = True
        self.name_norm = (self.name or "").strip().lower()
        self.phone_norm = (self.phone or "").strip()
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = set(update_fields)
            if "legal_entity_type" in update_fields or "legal_entity_type_id" in update_fields:
                update_fields.add("legal_entity_type")
                update_fields.add("legal_entity_type_id")
                if self.legal_entity_type_id is not None:
                    update_fields.add("is_corporate")
            if "name" in update_fields:
                update_fields.add("name_norm")
            if "phone" in update_fields:
                update_fields.add("phone_norm")
            kwargs["update_fields"] = list(update_fields)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name!r} / {self.phone!r}"


class SalesOrder(models.Model):
    class State(models.TextChoices):
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        PAID = "paid", "Paid"
        VOID = "void", "Void"

    id = models.AutoField(primary_key=True)
    code = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="sales_orders",
    )
    partner = models.ForeignKey(
        Partner,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sales_orders",
    )
    project = models.ForeignKey(
        "sales.Project",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sales_orders",
    )
    table_number = models.ForeignKey(
        TableNumber,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sales_orders",
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
    # Legacy column exists in DB; default applied at POS save draft.
    order_type = models.CharField(max_length=20, blank=True, default="", db_index=True)

    class Meta:
        db_table = "sales_order"
        ordering = ["-time_transaction", "-id"]
        indexes = [
            models.Index(fields=["-update_at"], name="idx_so_update_at"),
            models.Index(
                fields=["state", "-update_at"],
                name="idx_so_state_update_at",
            ),
            models.Index(fields=["created_by"], name="idx_so_created_by"),
        ]

    def __str__(self) -> str:
        label = self.code or f"#{self.pk}"
        return f"{label} {self.state}"


class SalesOrderLine(models.Model):
    id = models.AutoField(primary_key=True)
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="sales_order_lines",
    )
    quantity = models.DecimalField(max_digits=20, decimal_places=2)
    unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    is_active = models.BooleanField(default=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sales_order_line"
        indexes = [
            models.Index(
                fields=["sales_order", "id"],
                name="idx_sol_order_id",
            ),
        ]


class SalesOrderLineTax(models.Model):
    id = models.AutoField(primary_key=True)
    sales_order_line = models.ForeignKey(
        SalesOrderLine,
        on_delete=models.CASCADE,
        related_name="line_taxes",
    )
    tax = models.ForeignKey(
        Tax,
        on_delete=models.PROTECT,
        related_name="sales_order_line_taxes",
    )
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sales_order_line_tax"
        constraints = [
            models.UniqueConstraint(
                fields=["sales_order_line", "tax"],
                name="sales_order_line_tax_sales_order_line_id_tax_id_key",
            ),
        ]


class Project(models.Model):
    """
    Sales Project.

    Stored in table ``project``. Code is generated as ``PRJ/mm-yyyy/nnnn``.
    """

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    partner = models.ForeignKey(
        Partner,
        on_delete=models.PROTECT,
        related_name="projects",
        db_column="partner_id",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "project"
        ordering = ["-update_at", "-id"]
