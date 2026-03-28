from datetime import datetime, timedelta
from datetime import time as time_cls

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models import DecimalField, F, Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAppAdministrator
from core.code_counter import allocate_project_code, allocate_sales_order_code
from core.mixins import SoftDeactivateDestroyMixin
from core.models import CodeCounter
from core.query_params import parse_date_range_from_request
from master.models import Product, TableNumber, Tax

from .models import Partner, Project, SalesOrder, SalesOrderLine, SalesOrderLineTax
from .partner_normalization import normalize_partner_name, normalize_partner_phone
from .serializers import (
    PARTNER_DUPLICATE_NAME_ERROR,
    PARTNER_DUPLICATE_TAX_ID_ERROR,
    PartnerSerializer,
    PosSaveDraftSerializer,
    ProjectSerializer,
    SalesOrderLineListSerializer,
    SalesOrderReadSerializer,
)


def _partner_integrity_validation_error(err):
    """Map DB unique violations to DRF field errors (PostgreSQL constraint names)."""
    s = str(err).lower()
    if (
        "tax_id" in s
        or "unique_partner_tax_id" in s
        or "unique_partner_tax_id_norm" in s
    ):
        return ValidationError({"tax_id": PARTNER_DUPLICATE_TAX_ID_ERROR})
    if "unique_name_norm_corporate" in s or "unique_name_corporate" in s:
        return ValidationError({"name": PARTNER_DUPLICATE_NAME_ERROR})
    return None


class PartnerViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    """Partner master CRUD (DELETE = soft delete)."""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PartnerSerializer
    queryset = Partner.objects.order_by("name", "phone", "id")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        # Include inactive partners for master UI (active / non-active tabs + reactivate PATCH).
        qs = super(SoftDeactivateDestroyMixin, self).get_queryset().order_by("name", "phone", "id")
        corp_raw = (self.request.query_params.get("is_corporate") or "").strip()
        if corp_raw in ("1", "true", "True", "yes", "on"):
            qs = qs.filter(is_corporate=True)
        elif corp_raw in ("0", "false", "False", "no", "off"):
            qs = qs.filter(is_corporate=False)

        active_raw = (self.request.query_params.get("is_active") or "").strip().lower()
        if active_raw in ("1", "true", "yes", "on"):
            qs = qs.filter(is_active=True)
        elif active_raw in ("0", "false", "no", "off"):
            qs = qs.filter(is_active=False)

        search_raw = (self.request.query_params.get("search") or "").strip()
        if search_raw:
            qs = qs.filter(
                Q(name__icontains=search_raw)
                | Q(phone__icontains=search_raw)
                | Q(address__icontains=search_raw)
                | Q(tax_id__icontains=search_raw)
                | Q(parent__name__icontains=search_raw)
                | Q(legal_entity_type__code__icontains=search_raw)
                | Q(legal_entity_type__name__icontains=search_raw)
            )

        return qs.select_related("parent", "legal_entity_type")

    def perform_create(self, serializer):
        try:
            return super().perform_create(serializer)
        except IntegrityError as e:
            mapped = _partner_integrity_validation_error(e)
            if mapped is not None:
                raise mapped from e
            raise

    def perform_update(self, serializer):
        try:
            return super().perform_update(serializer)
        except IntegrityError as e:
            mapped = _partner_integrity_validation_error(e)
            if mapped is not None:
                raise mapped from e
            raise


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
                raise ValidationError({"product_id": "That isn't a valid product id."})
            qs = qs.filter(product_id=pid)
        code_raw = (self.request.query_params.get("sales_order_code") or "").strip()
        if code_raw:
            qs = qs.filter(sales_order__code__icontains=code_raw)
        order_type_raw = (self.request.query_params.get("order_type") or "").strip()
        if order_type_raw:
            qs = qs.filter(sales_order__order_type__iexact=order_type_raw)
        start, end = parse_date_range_from_request(self.request)
        if start and end and start > end:
            raise ValidationError(
                {"date_range": "Start date can't be after the end date."}
            )
        if start:
            qs = qs.filter(sales_order__time_transaction__gte=start)
        if end:
            qs = qs.filter(sales_order__time_transaction__lte=end)
        return qs


class ProjectViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    """Sales project CRUD (DELETE = soft deactivate)."""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectSerializer
    queryset = Project.objects.select_related("partner").order_by("-update_at", "-id")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset().select_related("partner").order_by("-update_at", "-id")
        partner_raw = self.request.query_params.get("partner_id")
        if partner_raw not in (None, ""):
            try:
                pid = int(partner_raw)
            except (TypeError, ValueError):
                raise ValidationError({"partner_id": "That isn't a valid partner id."})
            qs = qs.filter(partner_id=pid)
        return qs

    def perform_create(self, serializer):
        # Always generate code on create.
        obj = serializer.save(code=allocate_project_code(timezone.now()))
        return obj


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
        raise ValidationError({"table": "Table has to be a number."})
    t = TableNumber.objects.filter(name=n, is_active=True).first()
    if not t:
        raise ValidationError({"table": "No active table with that number."})
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
    forced_order_type = None

    def _resolve_order_type(self, validated_data):
        raw = (self.forced_order_type or validated_data.get("order_type") or "retail").strip()
        if raw not in ("retail", "non_retail", "delivery_order"):
            raise ValidationError(
                {"order_type": 'Use "retail", "non_retail", or "delivery_order".'}
            )
        return raw

    @transaction.atomic
    def post(self, request):
        ser = PosSaveDraftSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        order_type = self._resolve_order_type(d)

        partner_existed = False
        partner = None
        if d.get("partner_id"):
            partner = Partner.objects.filter(pk=d["partner_id"], is_active=True).first()
            if not partner:
                raise ValidationError({"partner_id": "That customer isn't there or is inactive."})
        else:
            partner, partner_existed = _upsert_partner_for_sales(
                d.get("customer_name", ""),
                d.get("customer_phone", ""),
            )

        project_obj = None
        if d.get("project_id"):
            project_obj = Project.objects.filter(pk=d["project_id"], is_active=True).first()
            if not project_obj:
                raise ValidationError({"project_id": "That project isn't there or is inactive."})

        if order_type in ("non_retail", "delivery_order"):
            if not partner:
                raise ValidationError(
                    {"partner_id": "You need a customer for this order type."}
                )
            if not partner.is_corporate:
                raise ValidationError(
                    {"partner_id": "This flow needs a corporate customer."}
                )
            if not project_obj:
                raise ValidationError(
                    {"project_id": "You need a project for this order type."}
                )
            if project_obj.partner_id != partner.id:
                raise ValidationError(
                    {"project_id": "That project doesn't go with this customer."}
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
                    {"sales_order_id": "Can't find that draft or you can't edit it."}
                )
            if not d.get("append_line") and not line_id:
                so.lines.filter(is_active=True).update(is_active=False)
            so.partner = partner
            so.project = project_obj
            so.table_number = table_obj
            so.time_transaction = d["transaction_at"]
            so.state = SalesOrder.State.DRAFT
            so.order_type = order_type
            so.save()
        else:
            so = SalesOrder.objects.create(
                code=allocate_sales_order_code(d["transaction_at"]),
                created_by=user,
                partner=partner,
                project=project_obj,
                table_number=table_obj,
                time_transaction=d["transaction_at"],
                state=SalesOrder.State.DRAFT,
                order_type=order_type,
            )

        product = Product.objects.get(pk=d["product_id"])
        if line_id:
            line = so.lines.filter(pk=line_id, is_active=True).first()
            if not line:
                raise ValidationError({"sales_order_line_id": "Couldn't find that line."})
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
            tax_ids = d.get("tax_ids") or []
            if not tax_ids and d.get("ppn_tax_id"):
                tax_ids = [d["ppn_tax_id"]]
            taxes = list(Tax.objects.filter(pk__in=tax_ids, is_active=True))
            found_ids = {t.id for t in taxes}
            invalid_ids = [tid for tid in tax_ids if tid not in found_ids]
            if invalid_ids:
                raise ValidationError(
                    {"tax_ids": f"These taxes aren't valid or active: {invalid_ids}"}
                )
            for tax in taxes:
                SalesOrderLineTax.objects.create(sales_order_line=line, tax=tax)

        so.refresh_from_db()
        payload = SalesOrderReadSerializer(so).data
        if partner_existed:
            payload["customer_notice"] = "We matched an existing customer - using their profile."
        return Response(payload, status=status.HTTP_200_OK)


class NonRetailSaveDraftView(PosSaveDraftView):
    permission_classes = (permissions.IsAuthenticated,)
    forced_order_type = "non_retail"


class DeliveryOrderSaveDraftView(PosSaveDraftView):
    permission_classes = (permissions.IsAuthenticated,)
    forced_order_type = "delivery_order"


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
            .select_related("partner", "project", "table_number", "created_by")
            .prefetch_related("lines__product", "lines__line_taxes__tax")
            .order_by("-time_transaction", "-id")
        )
        product_raw = self.request.query_params.get("product_id")
        if product_raw not in (None, ""):
            try:
                pid = int(product_raw)
            except (TypeError, ValueError):
                raise ValidationError({"product_id": "That isn't a valid product id."})
            qs = qs.filter(lines__product_id=pid, lines__is_active=True).distinct()
        so_code_raw = (self.request.query_params.get("sales_order_code") or "").strip()
        if so_code_raw:
            qs = qs.filter(code__icontains=so_code_raw)
        order_type_raw = (self.request.query_params.get("order_type") or "").strip()
        if order_type_raw:
            qs = qs.filter(order_type__iexact=order_type_raw)
        start, end = parse_date_range_from_request(self.request)
        if start and end and start > end:
            raise ValidationError(
                {"date_range": "Start date can't be after the end date."}
            )
        if start:
            qs = qs.filter(time_transaction__gte=start)
        if end:
            qs = qs.filter(time_transaction__lte=end)
        return qs

    def perform_destroy(self, instance):
        if instance.state != SalesOrder.State.DRAFT:
            raise ValidationError({"detail": "Only drafts can be deleted."})
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
            raise ValidationError({"detail": "Only drafts can be confirmed."})
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
            raise ValidationError({"detail": "Only confirmed orders can go back to draft."})
        so.state = SalesOrder.State.DRAFT
        so.save()
        so.refresh_from_db()
        return Response(SalesOrderReadSerializer(so).data)

    @action(detail=True, methods=["post"], url_path="delete-line")
    @transaction.atomic
    def delete_line(self, request, pk=None):
        so = get_object_or_404(
            self._orders_scope().select_for_update(of=("self",)),
            pk=pk,
        )
        if so.state != SalesOrder.State.DRAFT:
            raise ValidationError({"detail": "You can only change lines on drafts."})
        line_id = request.data.get("sales_order_line_id")
        try:
            line_id = int(line_id)
        except (TypeError, ValueError):
            raise ValidationError({"sales_order_line_id": "Send a numeric line id."})
        line = so.lines.filter(pk=line_id, is_active=True).first()
        if not line:
            raise ValidationError({"sales_order_line_id": "Couldn't find that line."})
        line.is_active = False
        line.save(update_fields=["is_active", "update_at"])
        so.refresh_from_db()
        return Response(SalesOrderReadSerializer(so).data)


def _calendar_week_bounds_local():
    """Monday–Sunday of the current week in the active timezone."""
    today = timezone.localdate()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def _calendar_month_bounds_local():
    """First and last day of the current calendar month (local date)."""
    today = timezone.localdate()
    first = today.replace(day=1)
    if today.month == 12:
        next_month = first.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = first.replace(month=today.month + 1, day=1)
    last = next_month - timedelta(days=1)
    return first, last


def _daterange_inclusive(start_d, end_d):
    d = start_d
    while d <= end_d:
        yield d
        d += timedelta(days=1)


def _transaction_local_date(tx):
    """
    Calendar date in the active timezone.

    DB may still hold naive ``time_transaction`` (legacy). With ``USE_TZ``,
    ``localtime()`` rejects naive values — treat naive as wall time in
    ``TIME_ZONE``.
    """
    if tx is None:
        return None
    if timezone.is_naive(tx):
        tx = timezone.make_aware(tx, timezone.get_current_timezone())
    return timezone.localtime(tx).date()


def _dashboard_line_total_idr(line):
    """Line subtotal + line taxes as integer IDR (same rules as POS / line list)."""
    q = line.quantity
    p = line.unit_price
    if q is None or p is None:
        return 0
    sub = round(float(q) * float(p))
    tax = 0
    for lt in line.line_taxes.all():
        try:
            if not lt.tax_id:
                continue
            r = float(lt.tax.rate_percent or 0)
        except ObjectDoesNotExist:
            continue
        except (TypeError, ValueError, AttributeError):
            continue
        tax += round(sub * (r / 100.0))
    return sub + tax


def _stacked_area_subtotal_only(user, start_dt, end_dt, labels, idx_by_label):
    tz = timezone.get_current_timezone()
    rows = (
        SalesOrderLine.objects.filter(
            is_active=True,
            sales_order__is_active=True,
            sales_order__created_by=user,
            sales_order__time_transaction__gte=start_dt,
            sales_order__time_transaction__lte=end_dt,
        )
        .annotate(
            day=TruncDate("sales_order__time_transaction", tzinfo=tz),
        )
        .values("day", "product_id", "product__name")
        .annotate(
            amount=Sum(
                F("quantity") * F("unit_price"),
                output_field=DecimalField(max_digits=30, decimal_places=2),
            ),
        )
        .order_by("product_id", "day")
    )

    by_product = {}
    for row in rows:
        day = row["day"]
        if day is None:
            continue
        lab = day.isoformat() if hasattr(day, "isoformat") else str(day)
        if lab not in idx_by_label:
            continue
        pid = row["product_id"]
        pname = row["product__name"] or f"Product #{pid}"
        if pid not in by_product:
            by_product[pid] = {
                "name": pname,
                "data": [0] * len(labels),
            }
        i = idx_by_label[lab]
        amt = row["amount"] or 0
        by_product[pid]["data"][i] += int(round(float(amt)))
    return by_product


def _stacked_area_with_taxes(user, start_dt, end_dt, labels, idx_by_label):
    qs = (
        SalesOrderLine.objects.filter(
            is_active=True,
            sales_order__is_active=True,
            sales_order__created_by=user,
            sales_order__time_transaction__gte=start_dt,
            sales_order__time_transaction__lte=end_dt,
        )
        .select_related("product", "sales_order")
        .prefetch_related("line_taxes__tax")
    )
    by_product = {}
    # Do not use ``iterator()`` here: it skips ``prefetch_related`` for line taxes.
    for line in qs:
        tx = line.sales_order.time_transaction
        day = _transaction_local_date(tx)
        if day is None:
            continue
        lab = day.isoformat()
        if lab not in idx_by_label:
            continue
        pid = line.product_id
        try:
            pname = line.product.name if line.product_id else f"Product #{pid}"
        except ObjectDoesNotExist:
            # FK broken or RelatedObjectDoesNotExist — not Product.DoesNotExist
            pname = f"Product #{pid}"
        if pid not in by_product:
            by_product[pid] = {
                "name": pname,
                "data": [0] * len(labels),
            }
        i = idx_by_label[lab]
        by_product[pid]["data"][i] += _dashboard_line_total_idr(line)
    return by_product


class SalesDashboardStackedAreaView(APIView):
    """
    Aggregated sales per calendar day and product for dashboard charts.

    Query:
    - ``period=week`` (Mon–Sun) or ``period=month`` (current month).
    - ``include_taxes=1`` (optional): use line subtotal + line taxes (IDR int);
      otherwise qty × unit_price only (faster SQL aggregate).
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        period = (request.query_params.get("period") or "").strip().lower()
        if period == "week":
            start_d, end_d = _calendar_week_bounds_local()
        elif period == "month":
            start_d, end_d = _calendar_month_bounds_local()
        else:
            raise ValidationError(
                {"period": 'Use period=week or period=month.'},
            )

        raw_inc = (request.query_params.get("include_taxes") or "").strip().lower()
        include_taxes = raw_inc in ("1", "true", "yes", "on")

        tz = timezone.get_current_timezone()
        start_dt = timezone.make_aware(datetime.combine(start_d, time_cls.min), tz)
        end_dt = timezone.make_aware(datetime.combine(end_d, time_cls.max), tz)

        labels = [d.isoformat() for d in _daterange_inclusive(start_d, end_d)]
        idx_by_label = {lab: i for i, lab in enumerate(labels)}

        if include_taxes:
            by_product = _stacked_area_with_taxes(
                request.user, start_dt, end_dt, labels, idx_by_label
            )
        else:
            by_product = _stacked_area_subtotal_only(
                request.user, start_dt, end_dt, labels, idx_by_label
            )

        series = [
            {"name": by_product[pid]["name"], "data": by_product[pid]["data"]}
            for pid in sorted(by_product.keys(), key=lambda x: (by_product[x]["name"], x))
        ]

        return Response(
            {
                "period": period,
                "include_taxes": include_taxes,
                "labels": labels,
                "series": series,
            }
        )


class ClearSalesDevelopmentDataView(APIView):
    """
    Hard-delete sales data and reset SO document codes (development / UAT).
    Deletes in order: sales_order_line_tax → sales_order_line → sales_order →
    code_counter rows for family ``SO``.
    """

    permission_classes = (permissions.IsAuthenticated, IsAppAdministrator)

    @transaction.atomic
    def post(self, request):
        deleted = {}
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
                "detail": "Sales dev data wiped - counters reset too.",
                "deleted": deleted,
            },
            status=status.HTTP_200_OK,
        )
