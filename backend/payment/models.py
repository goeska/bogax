from django.conf import settings
from django.db import models


class Payment(models.Model):
    class TxType(models.TextChoices):
        INCOMING = "i", "Incoming"
        OUTGOING = "o", "Outgoing"

    id = models.BigAutoField(primary_key=True)
    tx_type = models.CharField(max_length=1, choices=TxType.choices, db_index=True)
    source_table = models.CharField(max_length=64, db_index=True)
    source_pk = models.BigIntegerField(db_index=True)
    reference_code = models.CharField(max_length=100, blank=True, default="")
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency_code = models.CharField(max_length=3, default="IDR")
    transaction_at = models.DateTimeField()
    note = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="payments",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment"
        indexes = [
            models.Index(fields=["tx_type", "source_table", "source_pk"], name="idx_pay_source"),
            models.Index(fields=["-transaction_at"], name="idx_pay_tx_at"),
            models.Index(fields=["created_by"], name="idx_pay_created_by"),
        ]


class PaymentWithSource(models.Model):
    id = models.BigIntegerField(primary_key=True)
    tx_type = models.CharField(max_length=1)
    source_table = models.CharField(max_length=64)
    source_pk = models.BigIntegerField()
    reference_code = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency_code = models.CharField(max_length=3)
    transaction_at = models.DateTimeField()
    note = models.TextField()
    created_by_id = models.IntegerField(null=True, blank=True)
    created_by_email = models.EmailField(blank=True, default="")
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    source_id = models.BigIntegerField(null=True, blank=True)
    source_code = models.CharField(max_length=100, blank=True, default="")
    source_state = models.CharField(max_length=20, blank=True, default="")
    source_transaction_at = models.DateTimeField(null=True, blank=True)
    source_party_name = models.CharField(max_length=100, blank=True, default="")
    source_party_phone = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        managed = False
        db_table = "payment_with_source"
