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
from programas.models import Ciclo
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

    #  Obtener ciclo actual de la sesión
    ciclo_id = request.session.get("ciclo_id")
    ciclo_actual = Ciclo.objects.filter(id=ciclo_id).first()

    if not ciclo_actual:
        messages.warning(request, "No se ha definido un ciclo actual en tu sesión.")
        return redirect(
            "gestion_ciclos"
        )  # Redirigir a una vista para seleccionar ciclo

    #  Filtrar actividades según el rol y el ciclo actual
    if request.user.role == "DOCENTE" and request.user.departamento:
        actividades = Actividad.objects.filter(
            departamento=request.user.departamento,
            ciclo=ciclo_actual,
        )
    else:
        actividades = (
            filter_actividades_by_role(request.user)
            .filter(ciclo=ciclo_actual)
            .select_related("meta", "responsable", "departamento")
        )

    #  Permisos
    puede_crear = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_editar = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_eliminar = request.user.role in ["ADMIN", "DOCENTE"]

    #  Formularios
    form = ActividadForm(user=request.user)
    evidencia_form = EvidenciaForm()
    abrir_modal_crear = False
    abrir_modal_editar = False
    actividad_editar_id = None
    evidencias_editar = None

    if request.method == "POST":
        #  Solicitud de reapertura
        if "solicitar_reapertura" in request.POST:
            actividad = get_object_or_404(
                Actividad, id=request.POST.get("actividad_id")
            )
            # Evitar duplicadas
            existe_solicitud = SolicitudReapertura.objects.filter(
                actividad=actividad, aprobada=False
            ).exists()

            if existe_solicitud:
                messages.warning(
                    request,
                    "Ya existe una solicitud pendiente de reapertura para esta actividad.",
                )
                return redirect("gestion_actividades")

            # Crear solicitud
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
                actividad = form.save(commit=False)
                actividad.ciclo = ciclo_actual

                actividad.save()

                for archivo in archivos:
                    Evidencia.objects.create(actividad=actividad, archivo=archivo)

                finalizar = request.POST.get("finalizar_actividad", None)

                # Si el usuario envió el campo
                if finalizar is not None:
                    actividad.estado = "Cumplida"
                    actividad.editable = False
                    actividad.save(update_fields=["estado", "editable"])
                    messages.success(request, "Actividad finalizada.")
                else:
                    # Si no se marcó finalizar, la actividad sigue activa
                    actividad.estado = "Activa"
                    actividad.editable = True
                    actividad.save(update_fields=["estado", "editable"])

                messages.success(request, "Actividad creada correctamente.")
                return redirect("gestion_actividades")

            print(form.errors)
            messages.error(request, "Por favor corrija los errores en el formulario.")
            abrir_modal_crear = True

        # EDITAR ACTIVIDAD
        elif "editar_actividad" in request.POST and puede_editar:
            actividad_id = request.POST.get("actividad_id")
            actividad = get_object_or_404(Actividad, id=actividad_id)

            if not actividad.editable:
                messages.error(
                    request,
                    "Esta actividad ya no se puede editar, solicite una reapertura.",
                )
                return redirect("gestion_actividades")

            form = ActividadForm(request.POST, instance=actividad)
            archivos = request.FILES.getlist("archivo_evidencia")

            if form.is_valid():
                actividad = form.save(commit=False)
                actividad.ciclo = ciclo_actual

                for archivo in archivos:
                    Evidencia.objects.create(actividad=actividad, archivo=archivo)

                # Si el usuario marcó finalizar_actividad
                finalizar = request.POST.get("editable", None)

                # Si el usuario envió el campo
                if finalizar is not None:
                    actividad.estado = "Cumplida"
                    actividad.editable = False
                    actividad.save(update_fields=["estado", "editable"])
                    messages.success(request, "Actividad finalizada.")
                else:
                    # Si no se marcó finalizar, la actividad sigue activa
                    actividad.estado = "Activa"
                    actividad.editable = True
                    actividad.save(update_fields=["estado", "editable"])

                actividad.save()

                messages.success(request, "Actividad editada correctamente.")
                return redirect("gestion_actividades")

            abrir_modal_editar = True
            actividad_editar_id = actividad_id
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
            "evidencias_editar": evidencias_editar,
        },
    )


@role_required("ADMIN", "APOYO", "DOCENTE")
def ver_actividades(request, meta_id):
    #  Obtener la meta
    meta = get_object_or_404(Meta, id=meta_id)

    #  Obtener el ciclo desde la sesión (o el activo por defecto)
    ciclo_id = request.session.get("ciclo_id")
    ciclo = None
    if ciclo_id:
        ciclo = Ciclo.objects.filter(id=ciclo_id).first()
    if not ciclo:
        ciclo = (
            Ciclo.objects.filter(activo=True).first()
            or Ciclo.objects.order_by("-fecha_inicio").first()
        )

    #  Filtrar actividades según la meta y el ciclo
    actividades_qs = Actividad.objects.filter(meta=meta, ciclo=ciclo)

    # Filtrar por rol del usuario (usa tu helper existente)
    actividades = filter_actividades_by_role(request.user, actividades_qs)

    #  Renderizar el template con los datos
    return render(
        request,
        "actividades/ver_actividades.html",
        {
            "meta": meta,
            "ciclo": ciclo,
            "actividades": actividades,
        },
    )


# YA NO SE USA, QUITAR DESPUES POR AHORA SOLO SE OCULTA EL BOTON PARA AGREGAR
# SE ENCUENTRA EN SEGUIMIENTO -> VER -> ACTIVIDADES
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
@role_required("ADMIN")
def solicitudes_reapertura(request):
    #  Obtener el ciclo activo desde la sesión
    ciclo_id = request.session.get("ciclo_id")

    #  Base QuerySet con select_related para evitar consultas duplicadas
    base_queryset = SolicitudReapertura.objects.select_related(
        "actividad", "usuario", "departamento"
    ).order_by("-fecha_solicitud")

    #  Filtrar por ciclo si está en sesión
    if ciclo_id:
        base_queryset = base_queryset.filter(actividad__ciclo_id=ciclo_id)

    #  Dividir solicitudes en terminadas y pendientes
    solicitudesTerminadas = base_queryset.filter(terminada=True)
    solicitudes = base_queryset.filter(terminada=False)

    # -----------------------------
    #  Procesar POST (aprobar o rechazar)
    # -----------------------------
    if request.method == "POST":
        solicitud_id = request.POST.get("solicitud_id")
        accion = request.POST.get("accion")  # "aprobar" o "rechazar"

        solicitud = get_object_or_404(SolicitudReapertura, id=solicitud_id)

        if accion == "aprobar":
            with transaction.atomic():
                solicitud.aprobada = True
                solicitud.terminada = True
                solicitud.save()

                # Reabrir la actividad
                solicitud.actividad.editable = True
                solicitud.actividad.save()

                messages.success(
                    request,
                    f"La actividad '{solicitud.actividad.descripcion}' fue reabierta correctamente.",
                )

        elif accion == "rechazar":
            with transaction.atomic():
                solicitud.aprobada = False
                solicitud.terminada = True
                solicitud.save()

                # Mantener la actividad bloqueada
                solicitud.actividad.editable = False
                solicitud.actividad.save()

                messages.info(
                    request,
                    f"La solicitud de reapertura de '{solicitud.actividad.descripcion}' fue rechazada.",
                )

        return redirect("solicitudes_reapertura")

    # -----------------------------
    #  Renderizar template
    # -----------------------------
    return render(
        request,
        "actividades/solicitudes_reapertura.html",
        {
            "solicitudes": solicitudes,
            "solicitudesTerminadas": solicitudesTerminadas,
            "solicitudes_pendientes_count": solicitudes.count(),
            "solicitudes_aprobadas_count": solicitudesTerminadas.count(),
        },
    )


# =====================PLAN DE TRABAJO=============================
@role_required("DOCENTE", "ADMIN", "APOYO")
def obtener_contexto_programa_trabajo(request, departamento_seleccionado):
    """
    Devuelve un contexto listo para usar en el template del Programa de Trabajo.
    Filtra actividades por departamento y ciclo.
    """
    user = request.user
    ciclo_seleccionado = request.session.get("ciclo_id")
    # ADMIN y APOYO
    if user.role in ["ADMIN", "APOYO"]:
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
                # Filtramos las actividades por ciclo
                actividades = meta.actividad_set.all()
                if ciclo_seleccionado:
                    actividades = actividades.filter(ciclo_id=ciclo_seleccionado)

                total = actividades.count()
                completadas = actividades.filter(estado="Cumplida").count()

                if total > 0:
                    porcentaje = round((completadas / total) * 100, 1)
                    porcentaje_int = int(round((completadas / total) * 100))
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
            "ciclos": Ciclo.objects.all(),
            "departamento_seleccionado": departamento_seleccionado,
            "ciclo_seleccionado": ciclo_seleccionado,
        }

    # DOCENTE
    # DOCENTE
    else:
        actividades_por_meta = {}

        if hasattr(user, "departamento") and user.departamento:
            actividades = Actividad.objects.filter(
                departamento=user.departamento,
                responsable=user,
            )
            if ciclo_seleccionado:
                actividades = actividades.filter(ciclo_id=ciclo_seleccionado)
        else:
            # En caso de que no tenga departamento asignado (raro, pero se cubre)
            actividades = Actividad.objects.all()
            if ciclo_seleccionado:
                actividades = actividades.filter(ciclo_id=ciclo_seleccionado)

        # Agrupar por meta
        metas = Meta.objects.filter(
            id__in=actividades.values_list("meta_id", flat=True)
        )

        for meta in metas:
            acts_meta = actividades.filter(meta=meta)
            total = acts_meta.count()
            completadas = acts_meta.filter(estado="Cumplida").count()

            if total > 0:
                porcentaje = round((completadas / total) * 100, 1)
                porcentaje_int = int(round((completadas / total) * 100))
            else:
                porcentaje = 0.0
                porcentaje_int = 0

            actividades_por_meta[meta] = {
                "actividades": acts_meta,
                "completadas": completadas,
                "total": total,
                "porcentaje": porcentaje,
                "porcentaje_int": porcentaje_int,
            }

        context = {
            "user": user,
            "actividades_por_meta": actividades_por_meta,
            "ciclos": Ciclo.objects.all(),
            "ciclo_seleccionado": ciclo_seleccionado,
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
        ciclo_id = self.request.query_params.get("ciclo")

        queryset = Actividad.objects.select_related(
            "meta", "ciclo", "departamento", "responsable"
        ).prefetch_related("evidencias", "riesgo_set")

        if ciclo_id:
            queryset = queryset.filter(ciclo_id=ciclo_id)

        if user.role in ["ADMIN", "APOYO", "INVITADO"]:
            return queryset
        elif user.role == "DOCENTE":
            return queryset.filter(departamento=user.departamento)

        return Actividad.objects.none()

    def get_permissions(self):
        role = getattr(self.request.user, "role", None)
        if role == "ADMIN":
            return [IsAdmin()]
        elif role == "APOYO":
            return [IsApoyo()]
        elif role == "DOCENTE":
            return [IsDocente()]
        elif role == "INVITADO":
            return [IsInvitado()]
        return [permissions.IsAuthenticated()]


class EvidenciaViewSet(viewsets.ModelViewSet):
    serializer_class = EvidenciaSerializer

    def get_queryset(self):
        user = self.request.user
        ciclo_id = self.request.query_params.get("ciclo")

        queryset = Evidencia.objects.select_related("actividad", "actividad__ciclo")

        if ciclo_id:
            queryset = queryset.filter(actividad__ciclo_id=ciclo_id)

        if user.role in ["ADMIN", "APOYO"]:
            return queryset
        elif user.role == "DOCENTE":
            return queryset.filter(actividad__departamento=user.departamento)
        elif user.role == "INVITADO":
            return queryset.none()
        return Evidencia.objects.none()

    def perform_create(self, serializer):
        serializer.save()


class SolicitudReaperturaViewSet(viewsets.ModelViewSet):
    serializer_class = SolicitudReaperturaSerializer

    def get_queryset(self):
        user = self.request.user
        ciclo_id = self.request.query_params.get("ciclo")

        queryset = SolicitudReapertura.objects.select_related(
            "actividad", "usuario", "departamento"
        )

        if ciclo_id:
            queryset = queryset.filter(actividad__ciclo_id=ciclo_id)

        if user.role in ["ADMIN", "APOYO"]:
            return queryset
        elif user.role == "DOCENTE":
            return queryset.filter(usuario=user)
        elif user.role == "INVITADO":
            return queryset.none()
        return SolicitudReapertura.objects.none()

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
