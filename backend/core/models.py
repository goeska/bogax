from django.db import models


class CodeCounter(models.Model):
    """
    Atomic per-(family, calendar year) sequence for human-readable document codes.
    Use counter_family e.g. ``SO`` (sales order), ``PO`` (purchase), etc.
    """

    counter_family = models.CharField(max_length=20, db_index=True)
    year = models.PositiveSmallIntegerField()
    last_value = models.PositiveIntegerField(default=0)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "code_counter"
        constraints = [
            models.UniqueConstraint(
                fields=["counter_family", "year"],
                name="code_counter_family_year_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.counter_family}/{self.year} → {self.last_value}"
