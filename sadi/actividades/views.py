from rest_framework import viewsets, permissions
from .serializers import (
    ActividadDetailSerializer,
    EvidenciaSerializer,
    SolicitudReaperturaSerializer,
)
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Actividad, Evidencia, SolicitudReapertura
from metas.models import Meta
from usuarios.models import Usuario
from .forms import ActividadForm, EvidenciaForm
from .utils import filter_actividades_by_role
from usuarios.permissions import IsAdmin, IsApoyo, IsDocente, IsInvitado
from usuarios.decorators import role_required
from departamentos.models import Departamento
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
import io


# =====================CRUD=====================
@role_required("ADMIN", "APOYO", "DOCENTE")
def gestion_actividades(request):
    departamentos = Departamento.objects.all()
    if request.user.role == "DOCENTE" and request.user.departamento:
        actividades = Actividad.objects.all().filter(
            departamento=request.user.departamento
        )
    else:
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
    evidencias_editar = None  # Inicializar la variable

    if request.method == "POST":
        # Solicitud de reapertura
        if "solicitar_reapertura" in request.POST:
            actividad = get_object_or_404(
                Actividad, id=request.POST.get("actividad_id")
            )
            from .models import SolicitudReapertura

            # 🔒 Validar si ya existe una solicitud pendiente
            existe_solicitud = SolicitudReapertura.objects.filter(
                actividad=actividad, aprobada=False
            ).exists()

            if existe_solicitud:
                messages.warning(
                    request,
                    "Ya existe una solicitud pendiente de reapertura para esta actividad.",
                )
                return redirect("gestion_actividades")

            # Si no existe, crear una nueva
            SolicitudReapertura.objects.create(
                actividad=actividad,
                usuario=request.user,
                departamento=request.user.departamento,
            )
            messages.success(request, "Solicitud enviada al administrador.")
            return redirect("gestion_actividades")

        # CREAR ACTIVIDAD
        if "crear_actividad" in request.POST and puede_crear:
            form = ActividadForm(request.POST)
            archivos = request.FILES.getlist("archivo_evidencia")
            if form.is_valid():
                actividad = form.save()
                for archivo in archivos:
                    Evidencia.objects.create(actividad=actividad, archivo=archivo)
                if archivos:
                    actividad.estado = form.cleaned_data["estado"]
                    actividad.editable = False
                    actividad.save()
                else:
                    actividad.estado = form.cleaned_data["estado"]
                    actividad.save()
                messages.success(request, "Actividad creada correctamente.")
                return redirect("gestion_actividades")
            else:
                messages.error(
                    request, "Por favor corrija los errores en el formulario."
                )
            abrir_modal_crear = True

        # EDITAR ACTIVIDAD
        elif "editar_actividad" in request.POST and puede_editar:
            actividad_id = request.POST.get("actividad_id")
            actividad = get_object_or_404(Actividad, id=actividad_id)
            # Seguridad: si no es editable, bloquear edición
            if not actividad.editable:
                messages.error(request, "Esta actividad no es editable.")
                return redirect("gestion_actividades")

            form = ActividadForm(request.POST, instance=actividad)
            archivos = request.FILES.getlist("archivo_evidencia")
            if form.is_valid():
                actividad.estado = form.cleaned_data["estado"]
                form.save()
                for archivo in archivos:
                    Evidencia.objects.create(actividad=actividad, archivo=archivo)
                if archivos:
                    actividad.editable = False
                    actividad.estado = "Cumplida"
                    actividad.save()

                messages.success(request, "Actividad editada correctamente.")
                return redirect("gestion_actividades")
            abrir_modal_editar = True
            actividad_editar_id = actividad_id
            # Obtener evidencias solo cuando se está editando
            evidencias_editar = actividad.evidencias.all()

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
            "evidencias_editar": evidencias_editar,  # Ahora siempre está definida
        },
    )


@role_required("ADMIN", "APOYO", "DOCENTE")
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


# ======================SOLICITUD DE APERTURA==============================
@role_required("ADMIN")  # solo admin puede entrar
def solicitudes_reapertura(request):
    solicitudes = SolicitudReapertura.objects.select_related(
        "actividad", "usuario", "departamento"
    ).order_by("-fecha_solicitud")

    if request.method == "POST":
        solicitud_id = request.POST.get("solicitud_id")
        accion = request.POST.get("accion")  # "aprobar" o "rechazar"

        solicitud = get_object_or_404(SolicitudReapertura, id=solicitud_id)

        if accion == "aprobar":
            with transaction.atomic():  # Asegura que ambas operaciones se completen juntas
                # Marcar solicitud como aprobada
                solicitud.aprobada = True
                solicitud.save()

                # Cambiar estado de la actividad
                solicitud.actividad.editable = True
                solicitud.actividad.save()

            messages.success(
                request,
                f"La actividad '{solicitud.actividad.descripcion}' fue reabierta correctamente.",
            )
        elif accion == "rechazar":
            messages.info(
                request,
                f"La solicitud de reapertura de '{solicitud.actividad.descripcion}' fue rechazada.",
            )

        return redirect("solicitudes_reapertura")

    return render(
        request,
        "actividades/solicitudes_reapertura.html",
        {
            "solicitudes": solicitudes,
        },
    )


# =====================PLAN DE TRABAJO=============================
@role_required("DOCENTE", "ADMIN", "APOYO")
def obtener_contexto_programa_trabajo(request, departamento_seleccionado):
    """
    Devuelve un context listo para usar en el template.
    Cada meta tendrá:
      - actividades (QuerySet)
      - completadas (int)
      - total (int)
      - porcentaje (float redondeado a 1 decimal) -> para mostrar texto
      - porcentaje_int (int) -> para width y aria-valuenow (sin comas)
    """
    user = request.user
    if request.user.role in ["ADMIN", "APOYO"]:
        departamentos = Departamento.objects.all()
        if departamento_seleccionado:
            departamentos = departamentos.filter(id=departamento_seleccionado)

        actividades_por_depto = {}

        for depto in departamentos:
            metas = Meta.objects.filter(departamento=depto).prefetch_related(
                "actividad_set"
            )
            actividades_por_depto[depto] = {}

            for meta in metas:
                actividades = meta.actividad_set.all()

                total = actividades.count()
                completadas = actividades.filter(estado="Cumplida").count()

                if total > 0:
                    porcentaje = round((completadas / total) * 100, 1)  # p.ej. 50.0
                    porcentaje_int = int(round((completadas / total) * 100))  # p.ej. 50
                else:
                    porcentaje = 0.0
                    porcentaje_int = 0

                actividades_por_depto[depto][meta] = {
                    "actividades": actividades,
                    "completadas": completadas,
                    "total": total,
                    "porcentaje": porcentaje,
                    "porcentaje_int": porcentaje_int,
                }

        context = {
            "user": user,
            "actividades_por_depto": actividades_por_depto,
            "departamentos": Departamento.objects.all(),
            "departamento_seleccionado": departamento_seleccionado,
        }

    else:
        # Docente u otros
        if hasattr(request.user, "departamento") and request.user.departamento:
            metas = Meta.objects.filter(
                departamento=request.user.departamento
            ).prefetch_related("actividad_set")
        else:
            metas = Meta.objects.all().prefetch_related("actividad_set")

        actividades_por_meta = {}

        for meta in metas:
            actividades = meta.actividad_set.all()
            total = actividades.count()
            completadas = actividades.filter(estado="Cumplida").count()

            if total > 0:
                porcentaje = round((completadas / total) * 100, 1)
                porcentaje_int = int(round((completadas / total) * 100))
            else:
                porcentaje = 0.0
                porcentaje_int = 0

            actividades_por_meta[meta] = {
                "actividades": actividades,
                "completadas": completadas,
                "total": total,
                "porcentaje": porcentaje,
                "porcentaje_int": porcentaje_int,
            }

        context = {
            "user": user,
            "actividades_por_meta": actividades_por_meta,
        }

    return context


@role_required("DOCENTE", "ADMIN", "APOYO")
def ProgramaTrabajo(request):
    departamento_seleccionado = request.GET.get("departamento", "")
    context = obtener_contexto_programa_trabajo(request, departamento_seleccionado)
    return render(request, "actividades/programa_trabajo.html", context)


@role_required("DOCENTE", "ADMIN", "APOYO")
def programa_trabajo_pdf(request):
    departamento_seleccionado = request.GET.get("departamento", "")
    context = obtener_contexto_programa_trabajo(request, departamento_seleccionado)

    html = render_to_string("actividades/programa_trabajo_pdf.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="programa_trabajo.pdf"'

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=response)
    if pisa_status.err:
        return HttpResponse("Error al generar PDF <pre>" + html + "</pre>")
    return response


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


class EvidenciaViewSet(viewsets.ModelViewSet):
    serializer_class = EvidenciaSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        (IsAdmin | IsApoyo | IsDocente | IsInvitado),
    ]  # Combine permissions with OR

    def get_queryset(self):
        user = self.request.user
        if user.role == "ADMIN" or user.role == "APOYO":
            return Evidencia.objects.all()
        elif user.role == "DOCENTE":
            return Evidencia.objects.filter(actividad__departamento=user.departamento)
        else:
            return Evidencia.objects.none()

    def perform_create(self, serializer):
        serializer.save()


class SolicitudReaperturaViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudReaperturaSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        (IsAdmin | IsApoyo | IsDocente | IsInvitado),
    ]

    def get_queryset(self):
        user = self.request.user
        if user.role == "ADMIN" or user.role == "APOYO":
            return SolicitudReapertura.objects.all()
        else:
            return SolicitudReapertura.objects.filter(usuario=user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
