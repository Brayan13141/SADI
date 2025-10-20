from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Usuario

admin.site.register(Usuario, SimpleHistoryAdmin)


class UsuarioAdmin(SimpleHistoryAdmin):
    list_display = ("id", "username", "email", "is_active", "last_login")
    list_filter = ("is_active", "is_staff", "date_joined")
    search_fields = ("username", "email")
    ordering = ("username",)
    list_per_page = 20
    date_hierarchy = "date_joined"  #       agrega un filtro de fechas arriba

    fieldsets = (
        (
            "Información básica",
            {"fields": ("username", "email", "password"), "classes": ("wide",)},
        ),
        (
            "Permisos",
            {
                "fields": ("is_active", "is_staff", "is_superuser", "groups"),
            },
        ),
        (
            "Fechas importantes",
            {
                "fields": ("last_login", "date_joined"),
            },
        ),
    )
