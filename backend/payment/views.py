from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

from core.query_params import parse_date_range_from_request

from .models import PaymentWithSource
from .serializers import PaymentReadSerializer


class PaymentPagination(PageNumberPagination):
    page_size = 50


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PaymentReadSerializer
    pagination_class = PaymentPagination

    def get_queryset(self):
        qs = PaymentWithSource.objects.filter(is_active=True).order_by("-transaction_at", "-id")
        user = self.request.user
        if not (
            user.is_staff
            or user.is_superuser
            or getattr(user, "role", None) == "administrator"
        ):
            qs = qs.filter(created_by_id=user.pk)
        tx = self.request.query_params.get("tx_type")
        if tx in ("i", "o"):
            qs = qs.filter(tx_type=tx)
        elif tx not in (None, ""):
            raise ValidationError({"tx_type": "Must be 'i' (incoming) or 'o' (outgoing)."})
        start, end = parse_date_range_from_request(self.request)
        if start and end and start > end:
            raise ValidationError(
                {"date_range": "date_from must be on or before date_to."}
            )
        if start:
            qs = qs.filter(transaction_at__gte=start)
        if end:
            qs = qs.filter(transaction_at__lte=end)
        return qs
