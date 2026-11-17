from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to users with the 'admin' role or is_staff.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == "admin" or request.user.is_staff or request.user.is_superuser)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access only to the owner of the object or an admin.
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == "admin" or request.user.is_staff:
            return True
        user_field = getattr(obj, "user", None)
        return user_field == request.user
