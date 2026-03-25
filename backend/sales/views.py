from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAppAdministrator
from core.code_counter import COUNTER_FAMILY_SALES_ORDER, allocate_sales_order_code
from core.mixins import SoftDeactivateDestroyMixin
from core.models import CodeCounter
from core.query_params import parse_date_range_from_request
from master.models import Product, TableNumber, Tax
from payment.models import Payment

from .models import Partner, SalesOrder, SalesOrderLine, SalesOrderLineTax
from .partner_normalization import normalize_partner_name, normalize_partner_phone
from .serializers import (
    PartnerSerializer,
    PosSaveDraftSerializer,
    SalesOrderLineListSerializer,
    SalesOrderReadSerializer,
)


class PartnerViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    """Partner master CRUD (DELETE = soft delete)."""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PartnerSerializer
    queryset = Partner.objects.order_by("name", "phone", "id")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


class SalesOrderLineViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only sales lines list with product/date filters for reporting."""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SalesOrderLineListSerializer

    def get_queryset(self):
        qs = (
            SalesOrderLine.objects.filter(
                is_active=True,
                sales_order__is_active=True,
                sales_order__created_by=self.request.user,
            )
            .select_related("sales_order", "product")
            .prefetch_related("line_taxes__tax")
            .order_by("-sales_order__time_transaction", "-sales_order_id", "-id")
        )
        product_raw = self.request.query_params.get("product_id")
        if product_raw not in (None, ""):
            try:
                pid = int(product_raw)
            except (TypeError, ValueError):
                raise ValidationError({"product_id": "Invalid integer."})
            qs = qs.filter(product_id=pid)
        code_raw = (self.request.query_params.get("sales_order_code") or "").strip()
        if code_raw:
            qs = qs.filter(sales_order__code__icontains=code_raw)
        start, end = parse_date_range_from_request(self.request)
        if start and end and start > end:
            raise ValidationError(
                {"date_range": "date_from must be on or before date_to."}
            )
        if start:
            qs = qs.filter(sales_order__time_transaction__gte=start)
        if end:
            qs = qs.filter(sales_order__time_transaction__lte=end)
        return qs


def _is_app_admin(user):
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_staff
            or user.is_superuser
            or getattr(user, "role", None) == "administrator"
        )
    )


def _resolve_table(table_raw: str):
    table_raw = (table_raw or "").strip()
    if not table_raw:
        return None
    try:
        n = int(table_raw)
    except ValueError:
        raise ValidationError({"table": "Use a numeric table number."})
    t = TableNumber.objects.filter(name=n, is_active=True).first()
    if not t:
        raise ValidationError({"table": "Table not found or inactive."})
    return t


def _upsert_partner_for_sales(name: str, phone: str):
    name = (name or "").strip()
    phone = (phone or "").strip()
    if not name and not phone:
        return None, False
    name_norm = normalize_partner_name(name)
    phone_norm = normalize_partner_phone(phone)
    obj = Partner.objects.filter(name_norm=name_norm, phone_norm=phone_norm).first()
    created = obj is None
    if created:
        obj = Partner.objects.create(
            name=name,
            phone=phone,
            is_customer=True,
            is_active=True,
        )
    # Ensure existing partner rows are activated as customer partners for sales.
    update_fields = []
    if not created:
        if (obj.name or "").strip() != name:
            obj.name = name
            update_fields.append("name")
        if (obj.phone or "").strip() != phone:
            obj.phone = phone
            update_fields.append("phone")
    if not obj.is_customer:
        obj.is_customer = True
        update_fields.append("is_customer")
    if not obj.is_active:
        obj.is_active = True
        update_fields.append("is_active")
    if update_fields:
        obj.save(update_fields=update_fields)
    # True means partner row already existed before this request.
    return obj, (not created)


def _sales_order_total_amount(order: SalesOrder):
    total = 0
    for line in order.lines.filter(is_active=True):
        sub = round(float(line.quantity) * float(line.unit_price))
        total += sub
        for lt in line.line_taxes.all():
            r = float(lt.tax.rate_percent)
            total += round(sub * (r / 100.0))
    return total


class PosSaveDraftView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        ser = PosSaveDraftSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        partner, partner_existed = _upsert_partner_for_sales(
            d.get("customer_name", ""),
            d.get("customer_phone", ""),
        )
        table_obj = _resolve_table(d.get("table", ""))

        user = request.user
        order_id = d.get("sales_order_id")
        line_id = d.get("sales_order_line_id")

        if order_id:
            so = (
                SalesOrder.objects.select_for_update()
                .filter(
                    pk=order_id,
                    state=SalesOrder.State.DRAFT,
                    is_active=True,
                    created_by=user,
                )
                .first()
            )
            if not so:
                raise ValidationError(
                    {"sales_order_id": "Draft not found or cannot be edited."}
                )
            if not d.get("append_line") and not line_id:
                so.lines.filter(is_active=True).update(is_active=False)
            so.partner = partner
            so.table_number = table_obj
            so.time_transaction = d["transaction_at"]
            so.state = SalesOrder.State.DRAFT
            so.save()
        else:
            so = SalesOrder.objects.create(
                code=allocate_sales_order_code(d["transaction_at"]),
                created_by=user,
                partner=partner,
                table_number=table_obj,
                time_transaction=d["transaction_at"],
                state=SalesOrder.State.DRAFT,
            )

        product = Product.objects.get(pk=d["product_id"])
        if line_id:
            line = so.lines.filter(pk=line_id, is_active=True).first()
            if not line:
                raise ValidationError({"sales_order_line_id": "Line not found."})
            line.product = product
            line.quantity = d["quantity"]
            line.unit_price = d["unit_price"]
            line.save(update_fields=["product", "quantity", "unit_price", "update_at"])
            line.line_taxes.all().delete()
        else:
            line = SalesOrderLine.objects.create(
                sales_order=so,
                product=product,
                quantity=d["quantity"],
                unit_price=d["unit_price"],
            )
        if d.get("apply_ppn"):
            tax = Tax.objects.filter(pk=d["ppn_tax_id"], is_active=True).first()
            if not tax:
                raise ValidationError({"ppn_tax_id": "Invalid or inactive tax."})
            SalesOrderLineTax.objects.create(sales_order_line=line, tax=tax)

        so.refresh_from_db()
        payload = SalesOrderReadSerializer(so).data
        if partner_existed:
            payload["customer_notice"] = "Customer already exists. Using existing data."
        return Response(payload, status=status.HTTP_200_OK)


class SalesOrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """List / detail own active orders; soft-delete; POST confirm on draft."""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SalesOrderReadSerializer

    def _orders_scope(self):
        """Same ownership filter as list/detail — no select_related (safe with FOR UPDATE)."""
        return SalesOrder.objects.filter(
            is_active=True,
            created_by=self.request.user,
        )

    def get_queryset(self):
        qs = (
            self._orders_scope()
            .select_related("partner", "table_number", "created_by")
            .prefetch_related("lines__product", "lines__line_taxes__tax")
            .order_by("-time_transaction", "-id")
        )
        product_raw = self.request.query_params.get("product_id")
        if product_raw not in (None, ""):
            try:
                pid = int(product_raw)
            except (TypeError, ValueError):
                raise ValidationError({"product_id": "Invalid integer."})
            qs = qs.filter(lines__product_id=pid, lines__is_active=True).distinct()
        so_code_raw = (self.request.query_params.get("sales_order_code") or "").strip()
        if so_code_raw:
            qs = qs.filter(code__icontains=so_code_raw)
        start, end = parse_date_range_from_request(self.request)
        if start and end and start > end:
            raise ValidationError(
                {"date_range": "date_from must be on or before date_to."}
            )
        if start:
            qs = qs.filter(time_transaction__gte=start)
        if end:
            qs = qs.filter(time_transaction__lte=end)
        return qs

    def perform_destroy(self, instance):
        if instance.state != SalesOrder.State.DRAFT:
            raise ValidationError({"detail": "Only draft orders can be deleted."})
        instance.is_active = False
        instance.save(update_fields=["is_active"])

    @action(detail=True, methods=["post"], url_path="confirm")
    @transaction.atomic
    def confirm(self, request, pk=None):
        """Set ``sales_order.state`` to ``confirmed`` (only from ``draft``)."""
        # Lock only ``sales_order`` rows — avoid select_related + SELECT FOR UPDATE
        # (PostgreSQL: "FOR UPDATE cannot be applied to the nullable side of an outer join").
        so = get_object_or_404(
            self._orders_scope().select_for_update(of=("self",)),
            pk=pk,
        )
        if so.state != SalesOrder.State.DRAFT:
            raise ValidationError({"detail": "Only draft orders can be confirmed."})
        so.state = SalesOrder.State.CONFIRMED
        so.save()
        so.refresh_from_db()
        return Response(SalesOrderReadSerializer(so).data)

    @action(detail=True, methods=["post"], url_path="reopen")
    @transaction.atomic
    def reopen(self, request, pk=None):
        """Set ``sales_order.state`` back to ``draft`` (only from ``confirmed``)."""
        so = get_object_or_404(
            self._orders_scope().select_for_update(of=("self",)),
            pk=pk,
        )
        if so.state != SalesOrder.State.CONFIRMED:
            raise ValidationError({"detail": "Only confirmed orders can be reopened."})
        so.state = SalesOrder.State.DRAFT
        so.save()
        so.refresh_from_db()
        return Response(SalesOrderReadSerializer(so).data)

    @action(detail=True, methods=["post"], url_path="payment")
    @transaction.atomic
    def payment(self, request, pk=None):
        """Create incoming payment for confirmed sales order and mark as paid."""
        so = get_object_or_404(
            self._orders_scope().select_for_update(of=("self",)),
            pk=pk,
        )
        if so.state != SalesOrder.State.CONFIRMED:
            raise ValidationError({"detail": "Payment can only be created for confirmed orders."})
        amount = _sales_order_total_amount(so)
        Payment.objects.create(
            tx_type=Payment.TxType.INCOMING,
            source_table="sales_order",
            source_pk=so.pk,
            reference_code=so.code or "",
            amount=amount,
            currency_code="IDR",
            transaction_at=so.time_transaction,
            note=f"Incoming payment from Sales Order #{so.pk}",
            created_by=request.user,
        )
        so.state = SalesOrder.State.PAID
        so.save(update_fields=["state", "update_at"])
        so.refresh_from_db()
        return Response(SalesOrderReadSerializer(so).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="delete-line")
    @transaction.atomic
    def delete_line(self, request, pk=None):
        so = get_object_or_404(
            self._orders_scope().select_for_update(of=("self",)),
            pk=pk,
        )
        if so.state != SalesOrder.State.DRAFT:
            raise ValidationError({"detail": "Only draft orders can be edited."})
        line_id = request.data.get("sales_order_line_id")
        try:
            line_id = int(line_id)
        except (TypeError, ValueError):
            raise ValidationError({"sales_order_line_id": "Required integer id."})
        line = so.lines.filter(pk=line_id, is_active=True).first()
        if not line:
            raise ValidationError({"sales_order_line_id": "Line not found."})
        line.is_active = False
        line.save(update_fields=["is_active", "update_at"])
        so.refresh_from_db()
        return Response(SalesOrderReadSerializer(so).data)


class ClearSalesDevelopmentDataView(APIView):
    """
    Hard-delete sales data and reset SO document codes (development / UAT).
    Deletes in order: payment (sales_order source) → sales_order_line_tax →
    sales_order_line → sales_order → code_counter rows for family ``SO``.
    """

    permission_classes = (permissions.IsAuthenticated, IsAppAdministrator)

    @transaction.atomic
    def post(self, request):
        deleted = {}
        qs_pay = Payment.objects.filter(source_table="sales_order")
        deleted["payments"] = qs_pay.count()
        qs_pay.delete()

        qs_tax = SalesOrderLineTax.objects.all()
        deleted["sales_order_line_taxes"] = qs_tax.count()
        qs_tax.delete()

        qs_line = SalesOrderLine.objects.all()
        deleted["sales_order_lines"] = qs_line.count()
        qs_line.delete()

        qs_so = SalesOrder.objects.all()
        deleted["sales_orders"] = qs_so.count()
        qs_so.delete()

        qs_cc = CodeCounter.objects.filter(counter_family=COUNTER_FAMILY_SALES_ORDER)
        deleted["code_counter_rows"] = qs_cc.count()
        qs_cc.delete()

        return Response(
            {
                "detail": "Sales development data cleared.",
                "deleted": deleted,
            },
            status=status.HTTP_200_OK,
        )
