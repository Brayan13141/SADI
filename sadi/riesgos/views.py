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
    ciclo_id = request.session.get("ciclo_id")  #  Ciclo actual guardado en la sesión

    # Base del queryset: riesgos con su actividad y ciclo relacionados
    riesgos = Riesgo.objects.select_related(
        "actividad", "actividad__ciclo", "actividad__departamento"
    )

    #  Filtrar por ciclo de la sesión (si existe)
    if ciclo_id:
        riesgos = riesgos.filter(actividad__ciclo_id=ciclo_id)

    #  Filtro adicional por rol
    if request.user.role == "DOCENTE":
        riesgos = riesgos.filter(actividad__departamento=request.user.departamento)

    # ================================
    # Formularios y permisos
    # ================================
    form = RiesgoForm(request.POST or None, user=request.user, ciclo_id=ciclo_id)

    abrir_modal_crear = False
    abrir_modal_editar = False
    riesgo_editar_id = None

    puede_crear = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_editar = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_eliminar = request.user.role in ["ADMIN", "DOCENTE"]

    # ================================
    #  CREAR RIESGO
    # ================================
    if request.method == "POST":
        if "crear_riesgo" in request.POST and puede_crear:
            form = RiesgoForm(request.POST, user=request.user)
            if form.is_valid():
                riesgo = form.save(commit=False)
                # Validar que la actividad pertenezca al ciclo activo
                if ciclo_id and riesgo.actividad.ciclo_id != ciclo_id:
                    messages.error(
                        request,
                        "La actividad seleccionada no pertenece al ciclo activo.",
                    )
                    abrir_modal_crear = True
                else:
                    riesgo.save()
                    messages.success(request, "Riesgo creado correctamente.")
                    return redirect("gestion_riesgos")
            else:
                abrir_modal_crear = True
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

        # ================================
        #  EDITAR RIESGO
        # ================================
        elif "editar_riesgo" in request.POST and puede_editar:
            riesgo_id = request.POST.get("riesgo_id")
            if riesgo_id:
                riesgo = get_object_or_404(Riesgo, id=riesgo_id)
                form = RiesgoForm(request.POST, instance=riesgo, user=request.user)
                if form.is_valid():
                    riesgo = form.save(commit=False)
                    # Verificar que la actividad siga en el ciclo activo
                    if ciclo_id and riesgo.actividad.ciclo_id != ciclo_id:
                        messages.error(
                            request, "No se puede asignar una actividad de otro ciclo."
                        )
                        abrir_modal_editar = True
                        riesgo_editar_id = riesgo_id
                    else:
                        riesgo.save()
                        messages.success(request, "Riesgo editado correctamente.")
                        return redirect("gestion_riesgos")
                else:
                    abrir_modal_editar = True
                    riesgo_editar_id = riesgo_id
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")

        # ================================
        #  ELIMINAR RIESGO
        # ================================
        elif "eliminar_riesgo" in request.POST and puede_eliminar:
            riesgo_id = request.POST.get("riesgo_id")
            if riesgo_id:
                riesgo = get_object_or_404(Riesgo, id=riesgo_id)
                riesgo.delete()
                messages.success(request, "Riesgo eliminado correctamente.")
            return redirect("gestion_riesgos")

    # ================================
    #  RENDER FINAL
    # ================================
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
    ciclo_id = request.session.get("ciclo_id")  # 🔹 Ciclo activo en sesión
    user = request.user

    # ==============================
    # FILTRO BASE DE RIESGOS
    # ==============================
    riesgos = Riesgo.objects.select_related("actividad", "actividad__ciclo")

    # 🔹 Filtrar por ciclo activo
    if ciclo_id:
        riesgos = riesgos.filter(actividad__ciclo_id=ciclo_id)

    # 🔹 Filtrar por rol
    if user.role == "DOCENTE":
        riesgos = riesgos.filter(actividad__departamento=user.departamento)

    # ==============================
    # FILTRO BASE DE MITIGACIONES
    # ==============================
    mitigaciones = Mitigacion.objects.select_related(
        "responsable", "riesgo", "riesgo__actividad", "riesgo__actividad__ciclo"
    )

    # 🔹 Filtrar por ciclo activo
    if ciclo_id:
        mitigaciones = mitigaciones.filter(riesgo__actividad__ciclo_id=ciclo_id)

    # 🔹 Filtrar por departamento si es docente
    if user.role == "DOCENTE":
        mitigaciones = mitigaciones.filter(
            riesgo__actividad__departamento=user.departamento
        )

    # ==============================
    # FORMULARIO
    # ==============================
    form = MitigacionForm(request.POST or None, user=user, ciclo_id=ciclo_id)
    abrir_modal_crear = False
    abrir_modal_editar = False
    mitigacion_editar_id = None

    # ==============================
    # PERMISOS
    # ==============================
    puede_crear = user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_editar = user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_eliminar = user.role in ["ADMIN", "DOCENTE"]

    # ==============================
    # MANEJO DE FORMULARIOS
    # ==============================
    if request.method == "POST":
        # CREAR
        if "crear_mitigacion" in request.POST and puede_crear:
            form = MitigacionForm(request.POST, user=user, ciclo_id=ciclo_id)
            if form.is_valid():
                form.save()
                messages.success(request, "Mitigación creada correctamente.")
                return redirect("gestion_mitigaciones")
            abrir_modal_crear = True
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        # EDITAR
        elif "editar_mitigacion" in request.POST and puede_editar:
            mitigacion_id = request.POST.get("mitigacion_id")
            if mitigacion_id:
                mitigacion = get_object_or_404(Mitigacion, id=mitigacion_id)
                form = MitigacionForm(
                    request.POST, instance=mitigacion, user=user, ciclo_id=ciclo_id
                )
                if form.is_valid():
                    form.save()
                    messages.success(request, "Mitigación editada correctamente.")
                    return redirect("gestion_mitigaciones")
                mitigacion_editar_id = mitigacion_id
                abrir_modal_editar = True
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

        # ELIMINAR
        elif "eliminar_mitigacion" in request.POST and puede_eliminar:
            mitigacion_id = request.POST.get("mitigacion_id")
            if mitigacion_id:
                mitigacion = get_object_or_404(Mitigacion, id=mitigacion_id)
                mitigacion.delete()
                messages.success(request, "Mitigación eliminada correctamente.")
            return redirect("gestion_mitigaciones")

    # ==============================
    # RENDER
    # ==============================
    return render(
        request,
        "riesgos/gestion_mitigaciones.html",
        {
            "riesgos": riesgos,
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
            return Riesgo.objects.filter(
                actividad__meta__departamento=user.departamento
            )
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
                riesgo__actividad__meta__departamento=user.departamento
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
