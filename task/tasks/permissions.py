from rest_framework.permissions import BasePermission
from .models import Profile

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_authenticated and request.user.profile.role == "superadmin"
        except Profile.DoesNotExist:
            return False

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_authenticated and request.user.profile.role == "admin"
        except Profile.DoesNotExist:
            return False
