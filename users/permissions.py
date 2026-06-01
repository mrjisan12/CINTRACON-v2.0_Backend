from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_staff:
            return True
        try:
            profile = request.user.profile
            return profile.role == 'admin' or bool(profile.is_admin)
        except Exception:
            return False
