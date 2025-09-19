from rest_framework import viewsets, permissions
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from usuarios.decorators import role_required
from .models import Riesgo, Mitigacion
from .serializers import RiesgoDetailSerializer, MitigacionDetailSerializer
from .forms import RiesgoForm, MitigacionForm

from usuarios.permissions import IsAdmin, IsApoyo, IsDocente, IsInvitado


@role_required("ADMIN", "APOYO", "DOCENTE")
def gestion_riesgos(request):
    riesgos = Riesgo.objects.all().select_related("meta")
    form = RiesgoForm()
    abrir_modal_crear = False
    abrir_modal_editar = False
    riesgo_editar_id = None

    # permisos según rol
    puede_crear = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_editar = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_eliminar = request.user.role in ["ADMIN", "DOCENTE"]

    if request.method == "POST":
        if "crear_riesgo" in request.POST and puede_crear:
            form = RiesgoForm(request.POST)
            if form.is_valid():
                form.save()  # cálculo automático en el modelo
                messages.success(request, "Riesgo creado correctamente.")
                return redirect("gestion_riesgos")
            abrir_modal_crear = True
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        elif "editar_riesgo" in request.POST and puede_editar:
            riesgo_id = request.POST.get("riesgo_id")
            if riesgo_id:
                try:
                    riesgo = get_object_or_404(Riesgo, id=riesgo_id)
                    form = RiesgoForm(request.POST, instance=riesgo)
                    if form.is_valid():
                        form.save()
                        messages.success(request, "Riesgo editado correctamente.")
                        return redirect("gestion_riesgos")
                    riesgo_editar_id = riesgo_id
                    abrir_modal_editar = True
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                except Exception as e:
                    messages.error(request, f"Error al editar: {str(e)}")

        elif "eliminar_riesgo" in request.POST and puede_eliminar:
            riesgo_id = request.POST.get("riesgo_id")
            if riesgo_id:
                riesgo = get_object_or_404(Riesgo, id=riesgo_id)
                riesgo.delete()
                messages.success(request, "Riesgo eliminado correctamente.")
            return redirect("gestion_riesgos")

    return render(
        request,
        "riesgos/gestion_riesgos.html",
        {
            "riesgos": riesgos,
            "form": form,
            "abrir_modal_crear": abrir_modal_crear,
            "abrir_modal_editar": abrir_modal_editar,
            "riesgo_editar_id": riesgo_editar_id,
        },
    )


@role_required("ADMIN", "APOYO", "DOCENTE")
def gestion_mitigaciones(request):
    mitigaciones = Mitigacion.objects.all().select_related("responsable", "riesgo")
    form = MitigacionForm()
    abrir_modal_crear = False
    abrir_modal_editar = False
    mitigacion_editar_id = None

    # permisos según rol
    puede_crear = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_editar = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_eliminar = request.user.role in ["ADMIN", "DOCENTE"]

    if request.method == "POST":
        if "crear_mitigacion" in request.POST and puede_crear:
            form = MitigacionForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Mitigación creada correctamente.")
                return redirect("gestion_mitigaciones")
            abrir_modal_crear = True
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        elif "editar_mitigacion" in request.POST and puede_editar:
            mitigacion_id = request.POST.get("mitigacion_id")
            if mitigacion_id:
                try:
                    mitigacion = get_object_or_404(Mitigacion, id=mitigacion_id)
                    form = MitigacionForm(request.POST, instance=mitigacion)
                    if form.is_valid():
                        form.save()
                        messages.success(request, "Mitigación editada correctamente.")
                        return redirect("gestion_mitigaciones")
                    mitigacion_editar_id = mitigacion_id
                    abrir_modal_editar = True
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                except Exception as e:
                    messages.error(request, f"Error al editar: {str(e)}")

        elif "eliminar_mitigacion" in request.POST and puede_eliminar:
            mitigacion_id = request.POST.get("mitigacion_id")
            if mitigacion_id:
                mitigacion = get_object_or_404(Mitigacion, id=mitigacion_id)
                mitigacion.delete()
                messages.success(request, "Mitigación eliminada correctamente.")
            return redirect("gestion_mitigaciones")

    return render(
        request,
        "riesgos/gestion_mitigaciones.html",
        {
            "mitigaciones": mitigaciones,
            "form": form,
            "abrir_modal_crear": abrir_modal_crear,
            "abrir_modal_editar": abrir_modal_editar,
            "mitigacion_editar_id": mitigacion_editar_id,
        },
    )


# ===================API===================
class RiesgoViewSet(viewsets.ModelViewSet):
    serializer_class = RiesgoDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "APOYO", "INVITADO"]:
            return Riesgo.objects.all()
        elif user.role == "DOCENTE":
            return Riesgo.objects.filter(meta__departamento=user.departamento)
        return Riesgo.objects.none()

    def get_permissions(self):
        if self.request.user.role == "ADMIN":
            return [IsAdmin()]
        elif self.request.user.role == "APOYO":
            return [IsApoyo()]
        elif self.request.user.role == "DOCENTE":
            return [IsDocente()]
        elif self.request.user.role == "INVITADO":
            return [IsInvitado()]
        return [permissions.IsAuthenticated()]


class MitigacionViewSet(viewsets.ModelViewSet):
    serializer_class = MitigacionDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "APOYO", "INVITADO"]:
            return Mitigacion.objects.all()
        elif user.role == "DOCENTE":
            return Mitigacion.objects.filter(
                riesgo__meta__departamento=user.departamento
            )
        return Mitigacion.objects.none()

    def get_permissions(self):
        if self.request.user.role == "ADMIN":
            return [IsAdmin()]
        elif self.request.user.role == "APOYO":
            return [IsApoyo()]
        elif self.request.user.role == "DOCENTE":
            return [IsDocente()]
        elif self.request.user.role == "INVITADO":
            return [IsInvitado()]
        return [permissions.IsAuthenticated()]
