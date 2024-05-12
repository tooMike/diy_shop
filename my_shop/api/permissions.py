from django.contrib.auth import get_user_model
from rest_framework import permissions


User = get_user_model()


class IsAdminStaffAuthorReadOnly(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or request.user.is_staff
            or obj.author == request.user
        )
