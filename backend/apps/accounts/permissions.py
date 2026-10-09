"""Permisos por rol usados en toda la API."""
from rest_framework.permissions import BasePermission


class EsAdmin(BasePermission):
    """Permite el acceso solo a usuarios con rol de administrador."""

    message = "Esta acción requiere rol de administrador."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.es_admin
        )
