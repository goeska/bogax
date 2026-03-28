from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from core.mixins import SoftDeactivateDestroyMixin

from .permissions import IsStaffOrAppAdmin
from .serializers import (
    AdminUserSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class AdminUserViewSet(SoftDeactivateDestroyMixin, viewsets.ModelViewSet):
    """Staff only. DELETE soft-deactivates (``is_active=False``); no POST (use register)."""

    queryset = User.objects.all().order_by("email")
    serializer_class = AdminUserSerializer
    permission_classes = (IsStaffOrAppAdmin,)
    http_method_names = ["get", "patch", "delete", "head", "options"]


class MeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class HealthView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response({"status": "ok", "service": "bogax-api"})


class ApiRootView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        base = request.build_absolute_uri("/api/").rstrip("/")
        return Response(
            {
                "service": "bogax-api",
                "message": "POST /api/auth/login/ for a JWT, then Authorization: Bearer <access>.",
                "endpoints": {
                    "health": f"{base}/health/",
                    "login": f"{base}/auth/login/",
                    "refresh_token": f"{base}/auth/refresh/",
                    "register": f"{base}/auth/register/",
                    "current_user": f"{base}/auth/me/",
                    "main_config": f"{base}/main-config/",
                    "product_categories": f"{base}/product-categories/",
                    "products": f"{base}/products/",
                    "table_numbers": f"{base}/table-numbers/",
                    "taxes": f"{base}/taxes/",
                    "units_of_measure": f"{base}/uoms/",
                    "users_admin": f"{base}/users/",
                    "users_list": f"{base}/users/",
                    "pos_save_draft": f"{base}/pos/save-draft/",
                    "partners": f"{base}/partners/",
                    "sales_order_lines": f"{base}/sales-order-lines/",
                    "sales_orders": f"{base}/sales-orders/",
                    "clear_sales_development_data": f"{base}/sales/clear-development-data/",
                    "purchase_pos_save_draft": f"{base}/purchase/pos/save-draft/",
                    "purchase_orders": f"{base}/purchase-orders/",
                    "purchase_order_lines": f"{base}/purchase-order-lines/",
                    "receiving_orders": f"{base}/receiving-orders/",
                },
            }
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
