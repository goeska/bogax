from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ClearSalesDevelopmentDataView,
    DeliveryOrderSaveDraftView,
    NonRetailSaveDraftView,
    PartnerViewSet,
    PosSaveDraftView,
    ProjectViewSet,
    SalesDashboardStackedAreaView,
    SalesOrderLineViewSet,
    SalesOrderViewSet,
)

router = DefaultRouter()
router.register(r"partners", PartnerViewSet, basename="partner")
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"sales-order-lines", SalesOrderLineViewSet, basename="sales-order-line")
router.register(r"sales-orders", SalesOrderViewSet, basename="sales-order")

urlpatterns = [
    path(
        "sales/dashboard/stacked-area/",
        SalesDashboardStackedAreaView.as_view(),
        name="sales-dashboard-stacked-area",
    ),
    path("pos/save-draft/", PosSaveDraftView.as_view(), name="pos-save-draft"),
    path(
        "sales/non-retail/save-draft/",
        NonRetailSaveDraftView.as_view(),
        name="sales-non-retail-save-draft",
    ),
    path(
        "sales/delivery-order/save-draft/",
        DeliveryOrderSaveDraftView.as_view(),
        name="sales-delivery-order-save-draft",
    ),
    path(
        "sales/clear-development-data/",
        ClearSalesDevelopmentDataView.as_view(),
        name="sales-clear-development-data",
    ),
    path("", include(router.urls)),
]
