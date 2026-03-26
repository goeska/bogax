from django.db import models


class MainConfig(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    is_restaurant = models.BooleanField(default=False)
    currency_code = models.CharField(max_length=3, null=True, blank=True)
    is_customer_maintained = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = "main_config"
        managed = False

    def __str__(self) -> str:
        return f"MainConfig(pk={self.id})"


class ProductCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "product_category"
        managed = False
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    # Existing column in DB: varchar(20) NOT NULL default 'storable'.
    product_type = models.CharField(max_length=20, default="storable")
    product_category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        db_column="product_category_id",
        related_name="products",
    )
    uom = models.ForeignKey(
        "Uom",
        on_delete=models.PROTECT,
        db_column="uom_id",
        related_name="products",
    )
    is_active = models.BooleanField(default=True)
    unit_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "product"
        managed = False
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TableNumber(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.SmallIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "table_number"
        managed = False
        ordering = ["name"]

    def __str__(self) -> str:
        return str(self.name)


class Tax(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    rate_percent = models.DecimalField(max_digits=20, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "tax"
        managed = False
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Uom(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "uom"
        managed = False
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Coa(models.Model):
    """
    Chart of Accounts (CoA) — 2-level hierarchy (parent → child).

    Stored in ``accounting_coa``.
    """

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )
    update_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "accounting_coa"
        managed = False
        ordering = ["code", "id"]
        indexes = [
            models.Index(fields=["parent", "code"], name="idx_coa_parent_code"),
            models.Index(fields=["is_active", "code"], name="idx_coa_active_code"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uniq_coa_code"),
        ]

    def __str__(self) -> str:
        if self.parent_id:
            return f"{self.code} {self.name} (child of {self.parent_id})"
        return f"{self.code} {self.name}"


class LegalEntityType(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "legal_entity_type"
        managed = False
        ordering = ["code", "id"]

    def __str__(self) -> str:
        return f"{self.code} {self.name}"
