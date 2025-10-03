# usuarios/permissions.py
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    # """Permiso total para ADMIN."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"


class IsApoyo(permissions.BasePermission):
    # """Permiso parcial para APOYO (crear/editar pero no eliminar)."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "APOYO"

    def has_object_permission(self, request, view, obj):
        # No permitir DELETE
        if request.method == "DELETE":
            return False
        return True


class IsDocente(permissions.BasePermission):
    # """Permisos para DOCENTE (limitado a su departamento)."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "DOCENTE"

    def has_object_permission(self, request, view, obj):
        # Verificar que el objeto pertenece a su departamento
        if hasattr(obj, "departamento"):
            return obj.departamento == request.user.departamento
        return True


class IsInvitado(permissions.BasePermission):
    # """Permiso de solo lectura para INVITADO."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "INVITADO"

    def has_object_permission(self, request, view, obj):
        # Solo GET/HEAD/OPTIONS
        return request.method in permissions.SAFE_METHODS
