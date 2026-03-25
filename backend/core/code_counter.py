"""Thread-safe document code allocation using :class:`~core.models.CodeCounter`."""

from django.db import IntegrityError, transaction
from django.utils import timezone

from core.models import CodeCounter

# Prefix / family keys
COUNTER_FAMILY_SALES_ORDER = "SO"
COUNTER_FAMILY_PURCHASE_ORDER = "PO"
COUNTER_FAMILY_RECEIVING_ORDER = "RO"


def next_sequence(counter_family: str, year: int) -> int:
    """
    Increment and return the next sequence number for ``(counter_family, year)``.
    One row per calendar year; sequence resets by using a new ``year`` row.
    Safe under concurrent requests (``SELECT FOR UPDATE`` on the counter row).
    """
    with transaction.atomic():
        # Inner atomic = savepoint so IntegrityError on duplicate insert does not
        # abort the whole transaction (PostgreSQL).
        try:
            with transaction.atomic():
                CodeCounter.objects.create(
                    counter_family=counter_family,
                    year=year,
                    last_value=0,
                )
        except IntegrityError:
            pass
        row = CodeCounter.objects.select_for_update().get(
            counter_family=counter_family,
            year=year,
        )
        row.last_value += 1
        row.save(update_fields=["last_value"])
        return row.last_value


def allocate_sales_order_code(time_transaction) -> str:
    """
    Build ``SO/mm-yyyy/nnnn`` where ``mm-yyyy`` comes from *time_transaction*
    (localized with :setting:`TIME_ZONE`) and ``nnnn`` is the per-calendar-year
    sequence (shared across months within that year).
    """
    local = timezone.localtime(time_transaction)
    year = local.year
    seq = next_sequence(COUNTER_FAMILY_SALES_ORDER, year)
    return f"SO/{local.month:02d}-{local.year}/{seq:04d}"


def allocate_purchase_order_code(time_transaction) -> str:
    """Build ``PO/mm-yyyy/nnnn`` with the same sequence policy as sales."""
    local = timezone.localtime(time_transaction)
    year = local.year
    seq = next_sequence(COUNTER_FAMILY_PURCHASE_ORDER, year)
    return f"PO/{local.month:02d}-{local.year}/{seq:04d}"


def allocate_receiving_order_code(received_date) -> str:
    """Build ``RO/mm-yyyy/nnnn`` using the receiving date."""
    local = timezone.localtime(received_date)
    year = local.year
    seq = next_sequence(COUNTER_FAMILY_RECEIVING_ORDER, year)
    return f"RO/{local.month:02d}-{local.year}/{seq:04d}"
