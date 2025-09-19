from rest_framework import viewsets, permissions
from .serializers import ActividadDetailSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Actividad, Evidencia
from metas.models import Meta
from usuarios.models import Usuario
from .forms import ActividadForm, EvidenciaForm
from .utils import filter_actividades_by_role
from usuarios.permissions import IsAdmin, IsApoyo, IsDocente, IsInvitado
from usuarios.decorators import role_required
from departamentos.models import Departamento


# =====================CRUD=====================
@role_required("ADMIN", "APOYO", "DOCENTE")
def gestion_actividades(request):
    departamentos = Departamento.objects.all()

    actividades = filter_actividades_by_role(request.user).select_related(
        "meta", "responsable"
    )

    puede_crear = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_editar = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_eliminar = request.user.role in ["ADMIN", "DOCENTE"]

    form = ActividadForm(user=request.user)
    evidencia_form = EvidenciaForm()
    abrir_modal_crear = False
    abrir_modal_editar = False
    actividad_editar_id = None

    if request.method == "POST":
        # Solicitud de reapertura
        if "solicitar_reapertura" in request.POST:
            actividad = get_object_or_404(
                Actividad, id=request.POST.get("actividad_id")
            )
            from .models import SolicitudReapertura

            SolicitudReapertura.objects.create(
                actividad=actividad,
                usuario=request.user,
                departamento=request.user.departamento,
            )
            messages.success(request, "Solicitud enviada al administrador.")
            return redirect("gestion_actividades")

        # CREAR ACTIVIDAD
        # CREAR ACTIVIDAD
        if "crear_actividad" in request.POST and puede_crear:
            form = ActividadForm(request.POST)
            archivos = request.FILES.getlist("archivo_evidencia")
            if form.is_valid():
                actividad = form.save()
                # Guardar archivos asociados
                for archivo in archivos:
                    Evidencia.objects.create(actividad=actividad, archivo=archivo)
                # Si hay archivos, marcar como completada
                if archivos:
                    actividad.estado = True
                    actividad.save()
                else:
                    actividad.editable = True  # Pendiente si no hay archivos
                    actividad.save()

                messages.success(request, "Actividad creada correctamente.")
                return redirect("gestion_actividades")
            abrir_modal_crear = True

        # EDITAR ACTIVIDAD
        # EDITAR ACTIVIDAD
        elif "editar_actividad" in request.POST and puede_editar:
            actividad_id = request.POST.get("actividad_id")
            actividad = get_object_or_404(Actividad, id=actividad_id)
            form = ActividadForm(request.POST, instance=actividad)
            archivos = request.FILES.getlist("archivo_evidencia")
            if form.is_valid():
                if request.user.role in ["ADMIN", "APOYO"]:
                    actividad.estado = form.cleaned_data["estado"]
                else:
                    actividad.estado = False  # Pendiente por defecto

                form.save()
                # Guardar nuevos archivos si existen
                for archivo in archivos:
                    Evidencia.objects.create(actividad=actividad, archivo=archivo)
                # Si se subieron archivos, marcar como completada
                if archivos:
                    actividad.estado = True
                    actividad.save()

                messages.success(request, "Actividad editada correctamente.")
                return redirect("gestion_actividades")
            abrir_modal_editar = True
            actividad_editar_id = actividad_id

        # ELIMINAR ACTIVIDAD
        elif "eliminar_actividad" in request.POST and puede_eliminar:
            actividad_id = request.POST.get("actividad_id")
            actividad = get_object_or_404(Actividad, id=actividad_id)
            actividad.delete()
            messages.success(request, "Actividad eliminada correctamente.")
            return redirect("gestion_actividades")

    return render(
        request,
        "actividades/gestion_actividades.html",
        {
            "actividades": actividades,
            "departamentos": departamentos,
            "form": form,
            "evidencia_form": evidencia_form,
            "abrir_modal_crear": abrir_modal_crear,
            "abrir_modal_editar": abrir_modal_editar,
            "actividad_editar_id": actividad_editar_id,
        },
    )


@role_required("ADMIN", "APOYO")
def ver_actividades(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id)
    actividades = filter_actividades_by_role(
        request.user, Actividad.objects.filter(meta=meta)
    )
    return render(
        request,
        "actividades/ver_actividades.html",
        {"meta": meta, "actividades": actividades},
    )


@role_required("ADMIN", "APOYO")
def agregar_actividad(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id)
    usuarios = Usuario.objects.all()

    if request.method == "POST":
        form = ActividadForm(request.POST)
        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.meta = meta
            actividad.save()
            messages.success(request, "Actividad creada correctamente.")
            return redirect("ver_actividades", meta_id=meta.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ActividadForm()

    return render(
        request,
        "actividades/agregar_actividad.html",
        {"meta": meta, "usuarios": usuarios, "form": form},
    )


# ===============================API===============================


class ActividadViewSet(viewsets.ModelViewSet):
    serializer_class = ActividadDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == "ADMIN":
            return Actividad.objects.all()
        elif user.role == "APOYO":
            return Actividad.objects.all()
        elif user.role == "DOCENTE":
            return Actividad.objects.filter(departamento=user.departamento)
        elif user.role == "INVITADO":
            return Actividad.objects.all()
        return Actividad.objects.none()

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
