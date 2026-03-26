from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CoaViewSet,
    LegalEntityTypeViewSet,
    MainConfigView,
    ProductCategoryViewSet,
    ProductViewSet,
    TableNumberViewSet,
    TaxViewSet,
    UomViewSet,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"product-categories", ProductCategoryViewSet, basename="productcategory")
router.register(r"table-numbers", TableNumberViewSet, basename="tablenumber")
router.register(r"taxes", TaxViewSet, basename="tax")
router.register(r"uoms", UomViewSet, basename="uom")
router.register(r"coas", CoaViewSet, basename="coa")
router.register(r"legal-entity-types", LegalEntityTypeViewSet, basename="legalentitytype")

urlpatterns = [
    path("main-config/", MainConfigView.as_view(), name="main-config"),
    path("", include(router.urls)),
]
