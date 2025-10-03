from .models import Actividad


def filter_actividades_by_role(user, queryset=None):

    # Filtra actividades según el rol del usuario.

    if queryset is None:
        queryset = Actividad.objects.all()

    if user.role in ["ADMIN", "APOYO"]:
        return queryset
    elif user.role == "DOCENTE":
        return queryset.filter(departamento=user.departamento)
    elif user.role == "INVITADO":
        return queryset  # solo lectura, no filtramos
    return Actividad.objects.none()
