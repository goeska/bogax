from django.db import transaction
from django.db.models import DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.code_counter import allocate_purchase_order_code, allocate_receiving_order_code
from core.query_params import parse_date_range_from_request
from master.models import Product, Tax
from sales.models import Partner
from sales.partner_normalization import normalize_partner_name, normalize_partner_phone

from .models import PurchaseOrder, PurchaseOrderLine, PurchaseOrderLineTax, ReceivingOrder
from .serializers import (
    PurchaseOrderReadSerializer,
    PurchaseOrderLineListSerializer,
    PurchaseSaveDraftSerializer,
    ReceivingOrderCreateSerializer,
    ReceivingOrderReadSerializer,
    ReceivingOrderUpdateSerializer,
)


_ALLOWED_PURCHASE_TAX_KEYS = {"ppn", "pph 21", "pph21", "pph 22", "pph22", "pph 23", "pph23"}


def _purchase_tax_map(ids):
    if not ids:
        return {}
    qs = Tax.objects.filter(pk__in=ids, is_active=True)
    out = {}
    for t in qs:
        key = " ".join(str(t.name or "").strip().lower().split())
        if key in _ALLOWED_PURCHASE_TAX_KEYS:
            out[t.id] = t
    return out


def _upsert_vendor_partner(name: str, phone: str):
    name = (name or "").strip()
    phone = (phone or "").strip()
    if not name:
        raise ValidationError({"vendor_name": "Vendor name is required."})
    name_norm = normalize_partner_name(name)
    phone_norm = normalize_partner_phone(phone)
    obj = Partner.objects.filter(name_norm=name_norm, phone_norm=phone_norm).first()
    created = obj is None
    if created:
        obj = Partner.objects.create(
            name=name,
            phone=phone,
            is_vendor=True,
            is_active=True,
        )
    update_fields = []
    if not created:
        if (obj.name or "").strip() != name:
            obj.name = name
            update_fields.append("name")
        if (obj.phone or "").strip() != phone:
            obj.phone = phone
            update_fields.append("phone")
    if not obj.is_vendor:
        obj.is_vendor = True
        update_fields.append("is_vendor")
    if not obj.is_active:
        obj.is_active = True
        update_fields.append("is_active")
    if update_fields:
        obj.save(update_fields=update_fields)
    return obj, (not created)


class PurchaseSaveDraftView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        ser = PurchaseSaveDraftSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        partner, vendor_existed = _upsert_vendor_partner(
            d.get("vendor_name", ""), d.get("vendor_phone", "")
        )

        user = request.user
        order_id = d.get("purchase_order_id")
        line_id = d.get("purchase_order_line_id")

        if order_id:
            po = (
                PurchaseOrder.objects.select_for_update()
                .filter(
                    pk=order_id,
                    state=PurchaseOrder.State.DRAFT,
                    is_active=True,
                    created_by=user,
                )
                .first()
            )
            if not po:
                raise ValidationError({"purchase_order_id": "Draft not found or cannot be edited."})
            if not d.get("append_line") and not line_id:
                po.lines.filter(is_active=True).update(is_active=False)
            po.partner = partner
            po.time_transaction = d["transaction_at"]
            po.state = PurchaseOrder.State.DRAFT
            po.save()
        else:
            po = PurchaseOrder.objects.create(
                code=allocate_purchase_order_code(d["transaction_at"]),
                created_by=user,
                partner=partner,
                time_transaction=d["transaction_at"],
                state=PurchaseOrder.State.DRAFT,
            )

        product = Product.objects.get(pk=d["product_id"])
        if line_id:
            line = po.lines.filter(pk=line_id, is_active=True).first()
            if not line:
                raise ValidationError({"purchase_order_line_id": "Line not found."})
            line.product = product
            line.quantity = d["quantity"]
            line.unit_price = d["unit_price"]
            line.save(update_fields=["product", "quantity", "unit_price", "update_at"])
            line.line_taxes.all().delete()
        else:
            line = PurchaseOrderLine.objects.create(
                purchase_order=po,
                product=product,
                quantity=d["quantity"],
                unit_price=d["unit_price"],
            )

        tax_map = _purchase_tax_map(d.get("tax_ids", []))
        if d.get("tax_ids") and len(tax_map) != len(set(d.get("tax_ids", []))):
            raise ValidationError({"tax_ids": "Only active PPN/PPH 21/22/23 taxes are allowed."})
        for tax in tax_map.values():
            PurchaseOrderLineTax.objects.create(purchase_order_line=line, tax=tax)

        po.refresh_from_db()
        payload = PurchaseOrderReadSerializer(po).data
        if vendor_existed:
            payload["vendor_notice"] = "Vendor already exists. Using existing data."
        return Response(payload, status=status.HTTP_200_OK)


class PurchaseOrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PurchaseOrderReadSerializer

    def _orders_scope(self):
        return PurchaseOrder.objects.filter(
            is_active=True,
            created_by=self.request.user,
        )

    def get_queryset(self):
        qs = (
            self._orders_scope()
            .select_related("created_by", "partner")
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
        po_code_raw = (self.request.query_params.get("purchase_order_code") or "").strip()
        if po_code_raw:
            qs = qs.filter(code__icontains=po_code_raw)
        start, end = parse_date_range_from_request(self.request)
        if start and end and start > end:
            raise ValidationError(
                {"date_range": "Tanggal mulai harus sama atau sebelum tanggal akhir."}
            )
        if start:
            qs = qs.filter(time_transaction__gte=start)
        if end:
            qs = qs.filter(time_transaction__lte=end)
        return qs

    def perform_destroy(self, instance):
        if instance.state != PurchaseOrder.State.DRAFT:
            raise ValidationError({"detail": "Only draft orders can be deleted."})
        instance.is_active = False
        instance.save(update_fields=["is_active"])

    @action(detail=True, methods=["post"], url_path="confirm")
    @transaction.atomic
    def confirm(self, request, pk=None):
        po = get_object_or_404(
            self._orders_scope().select_for_update(of=("self",)),
            pk=pk,
        )
        if po.state != PurchaseOrder.State.DRAFT:
            raise ValidationError({"detail": "Only draft orders can be confirmed."})
        po.state = PurchaseOrder.State.CONFIRMED
        po.save()
        po.refresh_from_db()
        return Response(PurchaseOrderReadSerializer(po).data)

    @action(detail=True, methods=["post"], url_path="reopen")
    @transaction.atomic
    def reopen(self, request, pk=None):
        po = get_object_or_404(
            self._orders_scope().select_for_update(of=("self",)),
            pk=pk,
        )
        if po.state != PurchaseOrder.State.CONFIRMED:
            raise ValidationError({"detail": "Only confirmed orders can be reopened."})
        po.state = PurchaseOrder.State.DRAFT
        po.save(update_fields=["state", "update_at"])
        po.refresh_from_db()
        return Response(PurchaseOrderReadSerializer(po).data)


class PurchaseOrderLineViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PurchaseOrderLineListSerializer

    def get_queryset(self):
        qs = (
            PurchaseOrderLine.objects.filter(
                is_active=True,
                purchase_order__is_active=True,
                purchase_order__created_by=self.request.user,
            )
            .select_related("purchase_order__partner", "product")
            .annotate(
                received_quantity=Coalesce(
                    Sum(
                        "receiving_orders__quantity_received",
                        filter=Q(receiving_orders__is_active=True),
                    ),
                    Value(0),
                    output_field=DecimalField(max_digits=20, decimal_places=2),
                ),
            )
            .annotate(
                outstanding_quantity=F("quantity") - F("received_quantity"),
            )
            .order_by("-purchase_order__time_transaction", "-purchase_order_id", "-id")
        )
        product_raw = self.request.query_params.get("product_id")
        if product_raw not in (None, ""):
            try:
                pid = int(product_raw)
            except (TypeError, ValueError):
                raise ValidationError({"product_id": "Invalid integer."})
            qs = qs.filter(product_id=pid)
        po_code_raw = (self.request.query_params.get("purchase_order_code") or "").strip()
        if po_code_raw:
            qs = qs.filter(purchase_order__code__icontains=po_code_raw)
        start, end = parse_date_range_from_request(self.request)
        if start and end and start > end:
            raise ValidationError({"date_range": "Tanggal mulai harus sama atau sebelum tanggal akhir."})
        if start:
            qs = qs.filter(purchase_order__time_transaction__gte=start)
        if end:
            qs = qs.filter(purchase_order__time_transaction__lte=end)
        return qs


class ReceivingOrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "create":
            return ReceivingOrderCreateSerializer
        if self.action in ("update", "partial_update"):
            return ReceivingOrderUpdateSerializer
        return ReceivingOrderReadSerializer

    def _scope(self):
        return ReceivingOrder.objects.filter(
            is_active=True,
            purchase_order_line__purchase_order__is_active=True,
            purchase_order_line__is_active=True,
            purchase_order_line__purchase_order__created_by=self.request.user,
        )

    def get_queryset(self):
        qs = self._scope().select_related(
            "purchase_order_line__product",
            "purchase_order_line__purchase_order__partner",
        )
        order_id_raw = self.request.query_params.get("purchase_order_id")
        if order_id_raw not in (None, ""):
            try:
                order_id = int(order_id_raw)
            except (TypeError, ValueError):
                raise ValidationError({"purchase_order_id": "Invalid integer."})
            qs = qs.filter(purchase_order_line__purchase_order_id=order_id)
        order_code_raw = (self.request.query_params.get("purchase_order_code") or "").strip()
        if order_code_raw:
            qs = qs.filter(purchase_order_line__purchase_order__code__icontains=order_code_raw)
        state_raw = (self.request.query_params.get("state") or "").strip().lower()
        if state_raw:
            allowed_states = {"draft", "confirmed"}
            if state_raw not in allowed_states:
                raise ValidationError({"state": "Invalid state. Use: draft or confirmed."})
            qs = qs.filter(state=state_raw)
        start, end = parse_date_range_from_request(self.request)
        if start and end and start > end:
            raise ValidationError({"date_range": "Tanggal mulai harus sama atau sebelum tanggal akhir."})
        if start:
            qs = qs.filter(received_date__gte=start)
        if end:
            qs = qs.filter(received_date__lte=end)
        return qs.order_by("-received_date", "-id")

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        line = (
            PurchaseOrderLine.objects.select_related("purchase_order")
            .filter(
                pk=d["purchase_order_line_id"],
                is_active=True,
                purchase_order__is_active=True,
                purchase_order__created_by=request.user,
            )
            .first()
        )
        if not line:
            raise ValidationError({"purchase_order_line_id": "Line not found."})
        if line.purchase_order.state not in (
            PurchaseOrder.State.CONFIRMED,
            PurchaseOrder.State.RECEIVED,
        ):
            raise ValidationError(
                {"detail": "Goods receipt is only allowed for confirmed or received purchase orders."}
            )
        obj = ReceivingOrder.objects.create(
            code=allocate_receiving_order_code(d.get("received_date") or line.purchase_order.time_transaction),
            purchase_order_line_id=line.id,
            quantity_received=d["quantity_received"],
            received_date=d.get("received_date") or line.purchase_order.time_transaction,
            state="draft",
            notes=d.get("notes") or "",
            is_active=True,
        )
        return Response(ReceivingOrderReadSerializer(obj).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.state != "draft":
            raise ValidationError({"detail": "Only draft receiving orders can be edited."})
        ser = self.get_serializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        line_id = d.get("purchase_order_line_id", instance.purchase_order_line_id)
        line = (
            PurchaseOrderLine.objects.select_related("purchase_order")
            .filter(
                pk=line_id,
                is_active=True,
                purchase_order__is_active=True,
                purchase_order__created_by=request.user,
            )
            .first()
        )
        if not line:
            raise ValidationError({"purchase_order_line_id": "Line not found."})
        instance.purchase_order_line_id = line.id
        if "quantity_received" in d:
            instance.quantity_received = d["quantity_received"]
        if "received_date" in d:
            instance.received_date = d["received_date"]
        instance.save()
        return Response(ReceivingOrderReadSerializer(instance).data)

    @action(detail=True, methods=["post"], url_path="confirm")
    @transaction.atomic
    def confirm(self, request, pk=None):
        obj = get_object_or_404(self._scope().select_for_update(of=("self",)), pk=pk)
        if obj.state != "draft":
            raise ValidationError({"detail": "Only draft receiving orders can be confirmed."})
        obj.state = "confirmed"
        obj.save(update_fields=["state", "update_at"])
        po = obj.purchase_order_line.purchase_order
        if po.state != PurchaseOrder.State.RECEIVED:
            po.state = PurchaseOrder.State.RECEIVED
            po.save(update_fields=["state", "update_at"])
        return Response(ReceivingOrderReadSerializer(obj).data)

    @action(detail=False, methods=["post"], url_path="bulk-confirm")
    @transaction.atomic
    def bulk_confirm(self, request):
        raw_ids = request.data.get("ids")
        if not isinstance(raw_ids, list) or not raw_ids:
            raise ValidationError({"ids": "Provide a non-empty list of ids."})
        ids = []
        for v in raw_ids:
            try:
                ids.append(int(v))
            except (TypeError, ValueError):
                raise ValidationError({"ids": "All ids must be integers."})
        qs = self._scope().select_for_update(of=("self",)).filter(pk__in=ids)
        requested = len(ids)
        found = qs.count()
        drafts = list(qs.filter(state="draft"))
        confirmed_count = 0
        for obj in drafts:
            obj.state = "confirmed"
            obj.save(update_fields=["state", "update_at"])
            po = obj.purchase_order_line.purchase_order
            if po.state != PurchaseOrder.State.RECEIVED:
                po.state = PurchaseOrder.State.RECEIVED
                po.save(update_fields=["state", "update_at"])
            confirmed_count += 1
        return Response(
            {
                "requested": requested,
                "found": found,
                "confirmed": confirmed_count,
                "skipped": found - confirmed_count,
            }
        )

    def perform_destroy(self, instance):
        if instance.state != "draft":
            raise ValidationError({"detail": "Only draft receiving orders can be deleted."})
        instance.is_active = False
        instance.save(update_fields=["is_active", "update_at"])
