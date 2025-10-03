from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*allowed_roles):

    # Decorador para vistas basadas en templates.
    # allowed_roles: lista de roles permitidos, ej: ["ADMIN", "APOYO"]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Debes iniciar sesión.")
                return redirect("account_login")
            if request.user.role not in allowed_roles:
                messages.error(
                    request,
                    "No tienes los permisos necesarios para acceder a esta página.",
                )
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
