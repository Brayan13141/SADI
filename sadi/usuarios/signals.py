# signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.db.models.signals import pre_save
from programas.models import Ciclo


@receiver(user_logged_in)
def set_default_ciclo(sender, user, request, **kwargs):
    # Buscar el ciclo activo (usando el campo 'estado' en lugar de 'activo')
    ciclo_activo = Ciclo.objects.filter(estado="Activo").first()
    if ciclo_activo:
        request.session["ciclo_id"] = ciclo_activo.id
        request.session["ciclo_nombre"] = ciclo_activo.nombre
    else:
        # Si no hay ciclo activo, buscar el más reciente
        ciclo_reciente = Ciclo.objects.order_by("-fecha_inicio").first()
        if ciclo_reciente:
            request.session["ciclo_id"] = ciclo_reciente.id
            request.session["ciclo_nombre"] = ciclo_reciente.nombre
        else:
            request.session["ciclo_id"] = None
            request.session["ciclo_nombre"] = "Sin ciclo activo"
