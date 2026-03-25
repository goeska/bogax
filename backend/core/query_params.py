"""Shared query parameter parsing for list APIs."""

from datetime import datetime, time

from django.utils import timezone
from django.utils.dateparse import parse_date


def parse_date_range_from_request(request):
    """
    Read ``date_from`` and ``date_to`` (YYYY-MM-DD) in the active Django timezone.

    Returns ``(start_dt, end_dt)`` where each may be ``None`` if not provided or invalid.
    """
    tz = timezone.get_current_timezone()
    start = None
    end = None
    raw_from = request.query_params.get("date_from")
    raw_to = request.query_params.get("date_to")
    if raw_from:
        d = parse_date(raw_from)
        if d:
            start = timezone.make_aware(datetime.combine(d, time.min), tz)
    if raw_to:
        d = parse_date(raw_to)
        if d:
            end = timezone.make_aware(datetime.combine(d, time.max), tz)
    return start, end
