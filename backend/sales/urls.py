from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ClearSalesDevelopmentDataView,
    PartnerViewSet,
    PosSaveDraftView,
    SalesOrderLineViewSet,
    SalesOrderViewSet,
)

router = DefaultRouter()
router.register(r"partners", PartnerViewSet, basename="partner")
router.register(r"sales-order-lines", SalesOrderLineViewSet, basename="sales-order-line")
router.register(r"sales-orders", SalesOrderViewSet, basename="sales-order")

urlpatterns = [
    path("pos/save-draft/", PosSaveDraftView.as_view(), name="pos-save-draft"),
    path(
        "sales/clear-development-data/",
        ClearSalesDevelopmentDataView.as_view(),
        name="sales-clear-development-data",
    ),
    path("", include(router.urls)),
]
