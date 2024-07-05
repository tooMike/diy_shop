from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class IsAdminStaffOwnerReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Доступ для чтения разрешен всем авторизированным пользователям.
    Доступ для изменения разрешен только админам и создателю.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or request.user.is_staff
            or obj.user == request.user
        )


class IsOwner(permissions.IsAuthenticated):
    """
    Доступ разрешен только создателю.
    """
    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user
        )
