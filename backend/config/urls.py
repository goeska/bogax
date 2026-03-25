from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/", include("master.urls")),
    path("api/", include("sales.urls")),
    path("api/", include("purchase.urls")),
    path("api/", include("payment.urls")),
]
