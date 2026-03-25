from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PurchaseOrderLineViewSet,
    PurchaseOrderViewSet,
    PurchaseSaveDraftView,
    ReceivingOrderViewSet,
)

router = DefaultRouter()
router.register(r"purchase-orders", PurchaseOrderViewSet, basename="purchase-order")
router.register(r"purchase-order-lines", PurchaseOrderLineViewSet, basename="purchase-order-line")
router.register(r"receiving-orders", ReceivingOrderViewSet, basename="receiving-order")

urlpatterns = [
    path("purchase/pos/save-draft/", PurchaseSaveDraftView.as_view(), name="purchase-pos-save-draft"),
    path("", include(router.urls)),
]
