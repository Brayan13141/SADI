from decimal import Decimal
import json
from urllib import request
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from usuarios.decorators import role_required
from usuarios.permissions import IsAdmin, IsApoyo, IsDocente, IsInvitado
from psycopg2 import IntegrityError
from rest_framework import viewsets, permissions
from departamentos.models import Departamento
from .models import Meta, AvanceMeta, MetaComprometida
from django.contrib.auth.decorators import login_required
from programas.models import Ciclo
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages
from .serializers import (
    MetaDetailSerializer,
    AvanceMetaSerializer,
    MetaComprometidaSerializer,
)
from .forms import (
    MetaForm,
    AvanceMetaForm,
    MetaComprometidaForm,
    AvanceMetaGeneralForm,
    MetaComprometidaGeneralForm,
)


@role_required("ADMIN", "APOYO")
def gestion_metas(request):
    metas = Meta.objects.select_related("proyecto", "departamento", "ciclo").all()
    ciclos = Ciclo.objects.all()

    # Obtener meta comprometida para cada meta
    for meta in metas:
        try:
            meta.metacomprometida = MetaComprometida.objects.get(meta=meta)
        except MetaComprometida.DoesNotExist:
            meta.metacomprometida = None

    form = MetaForm()
    abrir_modal_crear = False
    abrir_modal_editar = False
    meta_editar_id = None

    # Permisos según rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role in ["ADMIN"]

    if request.method == "POST":
        post_data = request.POST.copy()
        defaults = {
            "enunciado": "Por definir",
            "indicador": "Por definir",
            "unidadMedida": "Por definir",
            "metodoCalculo": "Por definir",
            "lineabase": 0,
            "metacumplir": 0,
            "variableB": 0,
            "porcentages": False,
        }
        for key, value in defaults.items():
            if key not in post_data:
                post_data[key] = value

        # Crear meta
        if "crear_meta" in request.POST and puede_crear:
            form = MetaForm(post_data)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "Meta creada correctamente.")
                    return redirect("gestion_metas")
                except Exception as e:
                    messages.error(request, f"Error al crear la meta: {str(e)}")
                    abrir_modal_crear = True
            else:
                abrir_modal_crear = True
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

        # Editar meta
        elif "editar_meta" in request.POST and puede_editar:
            meta_id = request.POST.get("meta_id")
            meta = get_object_or_404(Meta, id=meta_id)
            form = MetaForm(post_data, instance=meta)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "Meta actualizada correctamente.")
                    return redirect("gestion_metas")
                except Exception as e:
                    messages.error(request, f"Error al actualizar la meta: {str(e)}")
                    abrir_modal_editar = True
                    meta_editar_id = meta_id
            else:
                abrir_modal_editar = True
                meta_editar_id = meta_id
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")

        # Eliminar meta
        elif "eliminar_meta" in request.POST and puede_eliminar:
            meta_id = request.POST.get("meta_id")
            meta = get_object_or_404(Meta, id=meta_id)
            try:
                meta.delete()
                messages.success(request, "Meta eliminada correctamente.")
                return redirect("gestion_metas")
            except Exception as e:
                messages.error(request, f"Error al eliminar la meta: {str(e)}")

    return render(
        request,
        "metas/gestion_metas.html",
        {
            "metas": metas,
            "ciclos": ciclos,
            "form": form,
            "abrir_modal_crear": abrir_modal_crear,
            "abrir_modal_editar": abrir_modal_editar,
            "meta_editar_id": meta_editar_id,
        },
    )


# =============VISTAS PARA EDICION MASIVA=====================
@role_required("ADMIN", "APOYO", "DOCENTE")
def avance_meta_general_list(request):
    avances = AvanceMeta.objects.select_related("metaCumplir", "departamento").order_by(
        "-fecha_registro"
    )
    departamentos = Departamento.objects.all()
    metas = Meta.objects.select_related("departamento").all().order_by("id")
    avance_form = AvanceMetaGeneralForm()

    metas_con_departamentos = {
        meta.id: {
            "departamento_id": meta.departamento.id if meta.departamento else "",
            "departamento_nombre": (
                meta.departamento.nombre if meta.departamento else ""
            ),
            "clave": meta.clave,
            "nombre": meta.nombre,
        }
        for meta in metas
    }

    abrir_modal_avance = False
    modo_edicion = False
    avance_id = None

    # permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    if request.method == "POST":
        if "crear_avance" in request.POST and puede_crear:
            avance_form = AvanceMetaGeneralForm(request.POST)
            if avance_form.is_valid():
                avance_form.save()
                messages.success(request, "Avance registrado correctamente.")
                return redirect("avance_meta_general_list")
            abrir_modal_avance = True
            messages.error(request, "Error al registrar el avance.")

        elif "editar_avance" in request.POST and puede_editar:
            avance_id = request.POST.get("avance_id")
            avance = get_object_or_404(AvanceMeta, id=avance_id)
            avance_form = AvanceMetaGeneralForm(request.POST, instance=avance)
            if avance_form.is_valid():
                avance_form.save()
                messages.success(request, "Avance actualizado correctamente.")
                return redirect("avance_meta_general_list")
            abrir_modal_avance = True
            modo_edicion = True
            messages.error(request, "Error al editar el avance.")

        elif "eliminar_avance" in request.POST and puede_eliminar:
            avance_id = request.POST.get("avance_id")
            avance = get_object_or_404(AvanceMeta, id=avance_id)
            avance.delete()
            messages.success(request, "Avance eliminado correctamente.")
            return redirect("avance_meta_general_list")
        else:
            messages.error(request, "No tienes permiso para realizar esta acción.")

    return render(
        request,
        "metas/gestion_lista_avances.html",
        {
            "avances": avances,
            "metas": metas,
            "avance_form": avance_form,
            "abrir_modal_avance": abrir_modal_avance,
            "modo_edicion": modo_edicion,
            "avance_id": avance_id,
            "departamentos": departamentos,
            "metas_con_departamentos": json.dumps(metas_con_departamentos),
        },
    )


@role_required("ADMIN", "APOYO", "DOCENTE")
def meta_comprometida_general_list(request):
    comprometidas = MetaComprometida.objects.select_related("meta").all()
    comprometida_form = MetaComprometidaGeneralForm()
    metas_con_comprometida = MetaComprometida.objects.values_list("meta_id", flat=True)

    abrir_modal_comprometida = False
    modo_edicion = False
    comprometida_id = None

    # permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    if request.method == "POST":
        if "crear_comprometida" in request.POST and puede_crear:
            comprometida_form = MetaComprometidaGeneralForm(request.POST)
            if comprometida_form.is_valid():
                meta = comprometida_form.cleaned_data["meta"]
                if MetaComprometida.objects.filter(meta=meta).exists():
                    messages.error(
                        request,
                        "Ya existe una meta comprometida para esta meta principal.",
                    )
                    abrir_modal_comprometida = True
                else:
                    comprometida_form.save()
                    messages.success(request, "Meta comprometida creada correctamente.")
                    return redirect("meta_comprometida_general_list")
            else:
                abrir_modal_comprometida = True
                messages.error(request, "Error al crear la meta comprometida.")

        elif "editar_comprometida" in request.POST and puede_editar:
            comprometida_id = request.POST.get("comprometida_id")
            comp = get_object_or_404(MetaComprometida, id=comprometida_id)
            comprometida_form = MetaComprometidaGeneralForm(request.POST, instance=comp)
            if comprometida_form.is_valid():
                meta = comprometida_form.cleaned_data["meta"]
                if (
                    comp.meta != meta
                    and MetaComprometida.objects.filter(meta=meta).exists()
                ):
                    messages.error(
                        request,
                        "Ya existe una meta comprometida para esta meta principal.",
                    )
                    abrir_modal_comprometida = True
                    modo_edicion = True
                else:
                    comprometida_form.save()
                    messages.success(
                        request, "Meta comprometida actualizada correctamente."
                    )
                    return redirect("meta_comprometida_general_list")
            else:
                abrir_modal_comprometida = True
                modo_edicion = True
                messages.error(request, "Error al editar la meta comprometida.")

        elif "eliminar_comprometida" in request.POST and puede_eliminar:
            comprometida_id = request.POST.get("comprometida_id")
            comp = get_object_or_404(MetaComprometida, id=comprometida_id)
            comp.delete()
            messages.success(request, "Meta comprometida eliminada correctamente.")
            return redirect("meta_comprometida_general_list")
        else:
            messages.error(request, "No tienes permiso para realizar esta acción.")

    return render(
        request,
        "metas/gestion_lista_mComprometida.html",
        {
            "comprometidas": comprometidas,
            "comprometida_form": comprometida_form,
            "abrir_modal_comprometida": abrir_modal_comprometida,
            "modo_edicion": modo_edicion,
            "comprometida_id": comprometida_id,
            "metas_con_comprometida": list(metas_con_comprometida),
        },
    )


# ====================== VISTAS POR META ======================
@login_required
def gestion_meta_avances(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id)
    avances = AvanceMeta.objects.filter(metaCumplir=meta).order_by("-fecha_registro")
    avance_form = AvanceMetaForm(meta=meta)
    comprometida_form = MetaComprometidaForm()

    abrir_modal_avance = False

    # permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    if request.method == "POST":
        if "crear_avance" in request.POST and puede_crear:
            avance_form = AvanceMetaForm(request.POST, meta=meta)
            if avance_form.is_valid():
                avance = avance_form.save(commit=False)
                avance.metaCumplir = meta
                if meta.departamento:
                    avance.departamento = meta.departamento
                avance.save()
                messages.success(request, "Avance registrado correctamente.")
                return redirect("gestion_meta_avances", meta_id=meta.id)
            abrir_modal_avance = True
            messages.error(
                request, "Error al registrar el avance. Verifique los datos."
            )

        elif "editar_avance" in request.POST and puede_editar:
            avance_id = request.POST.get("avance_id")
            try:
                avance = get_object_or_404(AvanceMeta, id=avance_id, metaCumplir=meta)
                avance_form = AvanceMetaForm(request.POST, instance=avance, meta=meta)
                if avance_form.is_valid():
                    avance_form.save()
                    messages.success(request, "Avance actualizado correctamente.")
                    return redirect("gestion_meta_avances", meta_id=meta.id)
                abrir_modal_avance = True
                messages.error(
                    request, "Error al editar el avance. Verifique los datos."
                )
            except Exception as e:
                messages.error(request, "Error al editar el avance.")

        elif "eliminar_avance" in request.POST and puede_eliminar:
            avance_id = request.POST.get("avance_id")
            avance = get_object_or_404(AvanceMeta, id=avance_id, metaCumplir=meta)
            avance.delete()
            messages.success(request, "Avance eliminado correctamente.")
            return redirect("gestion_meta_avances", meta_id=meta.id)
        else:
            messages.error(request, "No tienes permiso para realizar esta acción.")

    return render(
        request,
        "metas/gestion_meta_avances.html",
        {
            "meta": meta,
            "avances": avances,
            "avance_form": avance_form,
            "comprometida_form": comprometida_form,
            "abrir_modal_avance": abrir_modal_avance,
        },
    )


@login_required
def gestion_meta_comprometida(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id)
    comprometida = MetaComprometida.objects.filter(meta=meta).first()
    comprometida_form = MetaComprometidaForm(initial={"meta": meta})

    abrir_modal_comprometida = False
    modo_edicion = False

    # permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    if request.method == "POST":
        if "crear_comprometida" in request.POST and puede_crear:
            comprometida_form = MetaComprometidaForm(request.POST)
            if comprometida_form.is_valid():
                if MetaComprometida.objects.filter(meta=meta).exists():
                    messages.error(
                        request, "Ya existe una meta comprometida para esta meta."
                    )
                    abrir_modal_comprometida = True
                else:
                    comprometida_form.save()
                    messages.success(request, "Meta comprometida creada correctamente.")
                    return redirect("gestion_meta_comprometida", meta_id=meta.id)
            else:
                abrir_modal_comprometida = True
                messages.error(request, "Error en el formulario. Verifica los datos.")

        elif "editar_comprometida" in request.POST and puede_editar:
            comprometida_id = request.POST.get("comprometida_id")
            comp = get_object_or_404(MetaComprometida, id=comprometida_id, meta=meta)
            comprometida_form = MetaComprometidaForm(request.POST, instance=comp)
            if comprometida_form.is_valid():
                try:
                    comprometida_form.save()
                    messages.success(
                        request, "Meta comprometida actualizada correctamente."
                    )
                    return redirect("gestion_meta_comprometida", meta_id=meta.id)
                except IntegrityError:
                    abrir_modal_comprometida = True
                    modo_edicion = True
                    messages.error(request, "Error al actualizar la meta comprometida.")
            else:
                abrir_modal_comprometida = True
                modo_edicion = True
                messages.error(request, "Error en el formulario. Verifica los datos.")

        elif "eliminar_comprometida" in request.POST and puede_eliminar:
            comprometida_id = request.POST.get("comprometida_id")
            comp = get_object_or_404(MetaComprometida, id=comprometida_id, meta=meta)
            try:
                comp.delete()
                messages.success(request, "Meta comprometida eliminada correctamente.")
                return redirect("gestion_meta_comprometida", meta_id=meta.id)
            except Exception as e:
                messages.error(
                    request, f"Error al eliminar la meta comprometida: {str(e)}"
                )
        else:
            messages.error(request, "No tienes permiso para realizar esta acción.")

    return render(
        request,
        "metas/gestion_metaComprometida.html",
        {
            "meta": meta,
            "comprometida": comprometida,
            "comprometida_form": comprometida_form,
            "abrir_modal_comprometida": abrir_modal_comprometida,
            "modo_edicion": modo_edicion,
        },
    )


# ================VISTA PARA TABLA DE SEGUIMIENTO=========================
@role_required("ADMIN", "APOYO")
def TablaSeguimiento(request):
    # Obtener el ciclo activo o el más reciente
    ciclo = (
        Ciclo.objects.filter(activo=True).first()
        or Ciclo.objects.order_by("-fecha_inicio").first()
    )

    # Obtener todas las metas y ordenarlas
    metas = (
        Meta.objects.all().order_by("id")
        if request.GET.get("view") == "simple"
        else Meta.objects.filter(activa=True).order_by("id")
    )

    # Obtener lista de meses del ciclo
    meses = []
    if ciclo:
        current_date = ciclo.fecha_inicio
        while current_date <= ciclo.fecha_fin:
            meses.append(
                {
                    "nombre": current_date.strftime("%b"),
                    "numero": current_date.month,
                    "anio": current_date.year,
                }
            )
            # Avanzar un mes
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    else:
        # Si no hay ciclo activo, usar últimos 12 meses
        current_date = timezone.now()
        for i in range(12):
            month = current_date.month - i
            year = current_date.year
            if month <= 0:
                month += 12
                year -= 1
            meses.append(
                {
                    "nombre": timezone.datetime(year, month, 1).strftime("%b"),
                    "numero": month,
                    "anio": year,
                }
            )
        meses.reverse()

    # Construir la tabla
    tabla = []
    for meta in metas:
        avances = AvanceMeta.objects.filter(metaCumplir=meta)

        # Total acumulado (suma de avances)
        total = avances.aggregate(total=Sum("avance"))["total"] or Decimal("0")

        # Calcular porcentaje de avance correctamente
        if meta.metacumplir and meta.metacumplir > 0:
            porcentaje = min(
                Decimal("100"), (total / meta.metacumplir) * Decimal("100")
            )
        else:
            porcentaje = Decimal("0")

        # Lista ordenada de avances por mes (como porcentaje)
        valores_por_mes = []
        for mes_info in meses:
            # Filtrar los avances de este mes y sumarlos
            avances_mes = avances.filter(
                fecha_registro__year=mes_info["anio"],
                fecha_registro__month=mes_info["numero"],
            ).aggregate(total_mes=Sum("avance"))["total_mes"] or Decimal("0")

            if avances_mes > 0:
                if meta.porcentages:
                    valor = avances_mes * Decimal("100")
                    avance_mes = f"{valor.quantize(Decimal('0.00'))} %"
                else:
                    avance_mes = f"{avances_mes.quantize(Decimal('0.00'))}"
            else:
                avance_mes = "-"

            valores_por_mes.append(avance_mes)

        # Actividades relacionadas
        actividades = meta.actividad_set.all()

        tabla.append(
            {
                "id": meta.id,
                "meta": meta,
                "valores_por_mes": valores_por_mes,
                "total": (
                    f"{(total * Decimal('100')).quantize(Decimal('0.00'))} %"
                    if meta.porcentages
                    else f"{total.quantize(Decimal('0.00'))}"
                ),
                "porcentaje": porcentaje.quantize(Decimal("0.00")),
                "actividades": actividades,
            }
        )

    context = {"tabla": tabla, "ciclo": ciclo, "meses": meses}

    template = (
        "metas/tablaSeg_Completa.html"
        if request.GET.get("view") == "simple"
        else "metas/tablaSeguimiento.html"
    )
    return render(request, template, context)


# ==========================ASIGNACION DE METAS=========================


@role_required("ADMIN", "APOYO")
def asignacion_metas(request):
    metas = Meta.objects.filter(activa=True).order_by("clave")
    ciclos = Ciclo.objects.all()
    departamentos = Departamento.objects.all()

    # Inicializar carrito en sesión
    if "carrito_metas" not in request.session:
        request.session["carrito_metas"] = []

    # Permisos por rol
    puede_asignar = request.user.role in ["ADMIN", "APOYO"]
    puede_remover = request.user.role in ["ADMIN", "APOYO"]
    puede_aplicar = request.user.role == "ADMIN"

    # Manejo AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        if request.method == "POST":
            data = json.loads(request.body)
            action = data.get("action")

            # Agregar meta al carrito
            if action == "add" and puede_asignar:
                meta_id = data.get("meta_id")
                if meta_id and meta_id not in request.session["carrito_metas"]:
                    request.session["carrito_metas"].append(meta_id)
                    request.session.modified = True
                    return JsonResponse(
                        {"status": "success", "message": "Meta agregada al carrito"}
                    )
                return JsonResponse(
                    {"status": "error", "message": "La meta ya está en el carrito"}
                )

            # Quitar meta del carrito
            elif action == "remove" and puede_remover:
                meta_id = data.get("meta_id")
                if meta_id in request.session["carrito_metas"]:
                    request.session["carrito_metas"].remove(meta_id)
                    request.session.modified = True
                    return JsonResponse(
                        {"status": "success", "message": "Meta removida del carrito"}
                    )
                return JsonResponse(
                    {"status": "error", "message": "La meta no está en el carrito"}
                )

            # Aplicar cambios en lote
            elif action == "apply" and puede_aplicar:
                ciclo_id = data.get("ciclo")
                departamento_id = data.get("departamento")
                meta_ids = data.get("metas", [])

                ciclo = Ciclo.objects.get(id=ciclo_id) if ciclo_id else None
                departamento = (
                    Departamento.objects.get(id=departamento_id)
                    if departamento_id
                    else None
                )

                updated_count = 0
                for meta_id in meta_ids:
                    try:
                        meta = Meta.objects.get(id=meta_id)
                        if ciclo:
                            meta.ciclo = ciclo
                        if departamento:
                            meta.departamento = departamento
                        meta.save()
                        updated_count += 1
                    except Meta.DoesNotExist:
                        continue

                # Vaciar carrito
                request.session["carrito_metas"] = []
                request.session.modified = True

                return JsonResponse(
                    {
                        "status": "success",
                        "message": f"Se actualizaron {updated_count} metas correctamente",
                    }
                )

            return JsonResponse(
                {"status": "error", "message": "Acción no permitida o sin permisos"}
            )

    # GET normal
    metas_carrito = Meta.objects.filter(id__in=request.session["carrito_metas"])

    context = {
        "metas": metas,
        "metas_carrito": metas_carrito,
        "ciclos": ciclos,
        "departamentos": departamentos,
    }
    return render(request, "metas/asignacion_metas.html", context)


# =========================API=============================


class MetaViewSet(viewsets.ModelViewSet):
    serializer_class = MetaDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "APOYO", "INVITADO"]:
            return Meta.objects.all()
        elif user.role == "DOCENTE":
            return Meta.objects.filter(departamento=user.departamento)
        return Meta.objects.none()

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


class AvanceMetaViewSet(viewsets.ModelViewSet):
    serializer_class = AvanceMetaSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "APOYO"]:
            return AvanceMeta.objects.all()
        elif user.role == "DOCENTE":
            return AvanceMeta.objects.filter(departamento=user.departamento)
        elif user.role == "INVITADO":
            return AvanceMeta.objects.all()  # solo lectura
        return AvanceMeta.objects.none()

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


class MetaComprometidaViewSet(viewsets.ModelViewSet):
    serializer_class = MetaComprometidaSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "APOYO"]:
            return MetaComprometida.objects.all()
        elif user.role == "DOCENTE":
            return MetaComprometida.objects.none()  # sin acceso
        elif user.role == "INVITADO":
            return MetaComprometida.objects.all()  # solo lectura
        return MetaComprometida.objects.none()

    def get_permissions(self):
        if self.request.user.role == "ADMIN":
            return [IsAdmin()]
        elif self.request.user.role == "APOYO":
            return [IsApoyo()]

        elif self.user.role == "DOCENTE":
            # solo autenticación básica, sin permisos adicionales
            return [permissions.IsAuthenticated()]
        elif self.user.role == "INVITADO":
            return [IsInvitado()]
        return [permissions.IsAuthenticated()]
