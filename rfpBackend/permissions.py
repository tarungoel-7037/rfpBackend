from rest_framework.permissions import BasePermission

from rfp.models import AccountsUserprofile


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_staff or user.is_superuser:
            return True

        profile = AccountsUserprofile.objects.filter(user_id=user.id).first()
        return bool(profile and profile.role == "admin")


class IsVendorRole(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        profile = AccountsUserprofile.objects.filter(user_id=user.id).first()
        return bool(profile and profile.role == "vendor")
