from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import SoftDeactivateDestroyMixin

from .models import MainConfig, Product, ProductCategory, TableNumber, Tax, Uom
from .serializers import (
    MainConfigReadSerializer,
    MainConfigUpdateSerializer,
    ProductCategorySerializer,
    ProductSerializer,
    TableNumberSerializer,
    TaxSerializer,
    UomSerializer,
)


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
        qs = super().get_queryset()
        cat = self.request.query_params.get("product_category_id")
        if cat is not None and str(cat).strip() != "":
            try:
                qs = qs.filter(product_category_id=int(cat))
            except (TypeError, ValueError):
                pass
        return qs


class ProductCategoryViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = (permissions.IsAuthenticated,)


class TableNumberViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    queryset = TableNumber.objects.all()
    serializer_class = TableNumberSerializer
    permission_classes = (permissions.IsAuthenticated,)


class TaxViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """List aktif saja (mixin) + optional filter nama.

        Setara query PPN::

            SELECT id, name, rate_percent FROM tax
            WHERE name ILIKE '%ppn%' AND is_active = true;

        (Nilai ``ppn`` lewat query param ``name_ilike``; ``is_active`` dari mixin.)
        Django ``name__icontains`` pada PostgreSQL memakai ``ILIKE '%' || value || '%'``.
        Kolom dikembalikan lewat :class:`TaxSerializer` — bukan persentase statis di API.
        """
        qs = super().get_queryset()
        raw = self.request.query_params.get("name_ilike")
        if raw is not None and str(raw).strip() != "":
            qs = qs.filter(name__icontains=str(raw).strip())
        return qs


class UomViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    queryset = Uom.objects.all()
    serializer_class = UomSerializer
    permission_classes = (permissions.IsAuthenticated,)
