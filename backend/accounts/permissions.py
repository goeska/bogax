from rest_framework import permissions


class IsAppAdministrator(permissions.BasePermission):
    """Only users with app role ``administrator`` (not staff/superuser by itself)."""

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        return getattr(u, "role", None) == "administrator"


class IsStaffOrAppAdmin(permissions.BasePermission):
    """Django staff/superuser or app role ``administrator``."""

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if u.is_staff or u.is_superuser:
            return True
        return getattr(u, "role", None) == "administrator"
