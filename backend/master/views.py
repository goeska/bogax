import re

from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import SoftDeactivateDestroyMixin

from .models import Coa, LegalEntityType, MainConfig, Product, ProductCategory, TableNumber, Tax, Uom
from .serializers import (
    CoaSerializer,
    LegalEntityTypeSerializer,
    MainConfigReadSerializer,
    MainConfigUpdateSerializer,
    PRODUCT_DUPLICATE_NAME_ERROR,
    ProductCategorySerializer,
    ProductSerializer,
    TAX_DUPLICATE_NAME_ERROR,
    UOM_DUPLICATE_NAME_ERROR,
    TableNumberSerializer,
    TaxSerializer,
    UomSerializer,
)

_TRUE_VALUES = ("1", "true", "yes", "on")
_FALSE_VALUES = ("0", "false", "no", "off")


def _apply_is_active_filter(qs, request):
    active_raw = (request.query_params.get("is_active") or "").strip().lower()
    if active_raw in _TRUE_VALUES:
        return qs.filter(is_active=True)
    if active_raw in _FALSE_VALUES:
        return qs.filter(is_active=False)
    return qs


def _first_non_empty_query_param(request, *keys):
    for key in keys:
        raw = (request.query_params.get(key) or "").strip()
        if raw:
            return raw
    return ""


class MainConfigView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        cfg = MainConfig.objects.get(pk=1)
        return Response(MainConfigReadSerializer(cfg).data)

    def patch(self, request):
        ser = MainConfigUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        cfg = MainConfig.objects.get(pk=1)
        data = ser.validated_data
        update_fields = []
        if "is_restaurant" in data:
            cfg.is_restaurant = data["is_restaurant"]
            update_fields.append("is_restaurant")
        if "is_customer_maintained" in data:
            cfg.is_customer_maintained = data["is_customer_maintained"]
            update_fields.append("is_customer_maintained")
        cfg.save(update_fields=update_fields)
        return Response(MainConfigReadSerializer(cfg).data)


class ProductViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related("product_category", "uom").all()
    serializer_class = ProductSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Include inactive rows for master UI tabs and reactivation via PATCH.
        qs = (
            super(SoftDeactivateDestroyMixin, self)
            .get_queryset()
            .select_related("product_category", "uom")
            .order_by("name", "id")
        )
        qs = _apply_is_active_filter(qs, self.request)
        cat = self.request.query_params.get("product_category_id")
        if cat is not None and str(cat).strip() != "":
            try:
                qs = qs.filter(product_category_id=int(cat))
            except (TypeError, ValueError):
                pass
        ptype = (self.request.query_params.get("product_type") or "").strip()
        if ptype:
            qs = qs.filter(product_type=ptype)
        ptypes_raw = (self.request.query_params.get("product_types") or "").strip()
        if ptypes_raw:
            ptypes = [p.strip() for p in ptypes_raw.split(",") if p.strip()]
            if ptypes:
                qs = qs.filter(product_type__in=ptypes)
        name_raw = (self.request.query_params.get("name") or "").strip()
        if name_raw:
            qs = qs.filter(name__icontains=name_raw)
        return qs

    def perform_create(self, serializer):
        try:
            return super().perform_create(serializer)
        except IntegrityError as e:
            if _is_product_name_norm_unique_violation(e):
                raise ValidationError({"name": PRODUCT_DUPLICATE_NAME_ERROR}) from e
            raise

    def perform_update(self, serializer):
        try:
            return super().perform_update(serializer)
        except IntegrityError as e:
            if _is_product_name_norm_unique_violation(e):
                raise ValidationError({"name": PRODUCT_DUPLICATE_NAME_ERROR}) from e
            raise


def _is_product_name_norm_unique_violation(err):
    return bool(
        re.search(r"ux_product_name_norm(?!_category)", str(err), re.IGNORECASE)
    )


class ProductCategoryViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Include inactive rows for master UI tabs and reactivation via PATCH.
        qs = super(SoftDeactivateDestroyMixin, self).get_queryset().order_by("name", "id")
        qs = _apply_is_active_filter(qs, self.request)
        name_raw = _first_non_empty_query_param(self.request, "name")
        if name_raw:
            qs = qs.filter(name__icontains=name_raw)
        return qs

    def perform_create(self, serializer):
        try:
            return super().perform_create(serializer)
        except IntegrityError as e:
            if _is_product_category_name_unique_violation(e):
                raise ValidationError(
                    {
                        "name": (
                            "That category name's already taken - try another "
                            "(upper/lower doesn't matter)."
                        )
                    }
                ) from e
            raise

    def perform_update(self, serializer):
        try:
            return super().perform_update(serializer)
        except IntegrityError as e:
            if _is_product_category_name_unique_violation(e):
                raise ValidationError(
                    {
                        "name": (
                            "That category name's already taken - try another "
                            "(upper/lower doesn't matter)."
                        )
                    }
                ) from e
            raise


def _is_product_category_name_unique_violation(err):
    s = str(err).lower()
    return "ux_product_category_name_norm" in s or "ux_product_category_name" in s


class TableNumberViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    queryset = TableNumber.objects.all()
    serializer_class = TableNumberSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Include inactive rows for master UI tabs and reactivation via PATCH.
        return super(SoftDeactivateDestroyMixin, self).get_queryset()

    def perform_create(self, serializer):
        try:
            return super().perform_create(serializer)
        except IntegrityError:
            raise ValidationError(
                {
                    "name": (
                        "That table number's already in use (even on inactive rows). "
                        "Try another number or turn the old one active again."
                    )
                }
            )

    def perform_update(self, serializer):
        try:
            return super().perform_update(serializer)
        except IntegrityError:
            raise ValidationError(
                {
                    "name": (
                        "That table number's already in use (even on inactive rows). "
                        "Try another number or turn the old one active again."
                    )
                }
            )


class TaxViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Include inactive rows for master UI tabs and reactivation via PATCH.
        qs = super(SoftDeactivateDestroyMixin, self).get_queryset().order_by("name", "id")
        qs = _apply_is_active_filter(qs, self.request)
        name_raw = _first_non_empty_query_param(self.request, "name", "name_ilike")
        if name_raw:
            qs = qs.filter(name__icontains=name_raw)
        return qs

    def perform_create(self, serializer):
        try:
            return super().perform_create(serializer)
        except IntegrityError as e:
            if _is_tax_name_norm_unique_violation(e):
                raise ValidationError({"name": TAX_DUPLICATE_NAME_ERROR}) from e
            raise

    def perform_update(self, serializer):
        try:
            return super().perform_update(serializer)
        except IntegrityError as e:
            if _is_tax_name_norm_unique_violation(e):
                raise ValidationError({"name": TAX_DUPLICATE_NAME_ERROR}) from e
            raise


def _is_tax_name_norm_unique_violation(err):
    return "ux_tax_name_norm" in str(err).lower()


class UomViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    queryset = Uom.objects.all()
    serializer_class = UomSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Include inactive rows for master UI tabs and reactivation via PATCH.
        qs = super(SoftDeactivateDestroyMixin, self).get_queryset().order_by("name", "id")
        qs = _apply_is_active_filter(qs, self.request)
        name_raw = _first_non_empty_query_param(self.request, "name")
        if name_raw:
            qs = qs.filter(name__icontains=name_raw)
        return qs

    def perform_create(self, serializer):
        try:
            return super().perform_create(serializer)
        except IntegrityError as e:
            if _is_uom_name_norm_unique_violation(e):
                raise ValidationError({"name": UOM_DUPLICATE_NAME_ERROR}) from e
            raise

    def perform_update(self, serializer):
        try:
            return super().perform_update(serializer)
        except IntegrityError as e:
            if _is_uom_name_norm_unique_violation(e):
                raise ValidationError({"name": UOM_DUPLICATE_NAME_ERROR}) from e
            raise


def _is_uom_name_norm_unique_violation(err):
    return "ux_uom_name_norm" in str(err).lower()


class CoaViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    queryset = Coa.objects.select_related("parent").all()
    serializer_class = CoaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = super().get_queryset()
        parent_id = self.request.query_params.get("parent_id")
        if parent_id is not None and str(parent_id).strip() != "":
            try:
                qs = qs.filter(parent_id=int(parent_id))
            except (TypeError, ValueError):
                pass
        return qs


class LegalEntityTypeViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LegalEntityTypeSerializer
    queryset = LegalEntityType.objects.all().order_by("code", "id")
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        # SoftDeactivateDestroyMixin normally hides inactive rows; we need all rows for
        # the "Non Active Type" tab and for PATCH to reactivate (e.g. Yayasan).
        return super(SoftDeactivateDestroyMixin, self).get_queryset()

    def perform_create(self, serializer):
        try:
            return super().perform_create(serializer)
        except IntegrityError:
            raise ValidationError({"code": "That code's already in use - try a different one."})

    def perform_update(self, serializer):
        try:
            return super().perform_update(serializer)
        except IntegrityError:
            raise ValidationError({"code": "That code's already in use - try a different one."})
