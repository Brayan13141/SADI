from decimal import Decimal, InvalidOperation
import json
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from usuarios.decorators import role_required
from usuarios.permissions import IsAdmin, IsApoyo, IsDocente, IsInvitado
from psycopg2 import IntegrityError
from rest_framework import viewsets, permissions
from departamentos.models import Departamento
from .models import Meta, AvanceMeta, MetaComprometida, MetaCiclo
from programas.models import Ciclo
from proyectos.models import Proyecto
from django.db.models import Sum
from django.db import transaction
from core.models import ConfiguracionGlobal
from django.utils import timezone
from django.contrib import messages
from django.db.models import ProtectedError, RestrictedError
from .serializers import (
    MetaDetailSerializer,
    AvanceMetaSerializer,
    MetaComprometidaSerializer,
)
from .forms import (
    MetaFormAdmin,
    MetaFormDocente,
    AvanceMetaForm,
    MetaComprometidaForm,
    AvanceMetaGeneralForm,
    MetaComprometidaGeneralForm,
    AsignarCicloMetaForm,
)


@role_required("ADMIN", "APOYO", "DOCENTE")
def gestion_metas(request):

    ciclo_id = request.session.get("ciclo_id")

    usuario = request.user
    # --- 1. Cargar solo las metas globales (sin sus ciclos) ---
    if usuario.role == "ADMIN" or usuario.role == "APOYO":
        metas = Meta.objects.select_related("proyecto", "departamento").all()
    elif usuario.role == "DOCENTE":
        metas = Meta.objects.select_related("proyecto", "departamento").filter(
            departamento=usuario.departamento
        )

    for meta in metas:
        # Busca la MetaComprometida del ciclo
        comprometida = MetaCiclo.objects.filter(meta=meta, ciclo=ciclo_id).first()
        if meta.porcentages:
            meta.metaComprometida = (
                (comprometida.metaCumplir * Decimal("100")).quantize(Decimal("0.01"))
                if comprometida
                else None
            )
        else:
            meta.metaComprometida = (
                comprometida.metaCumplir.quantize(Decimal("0.01"))
                if comprometida
                else None
            )

    abrir_modal_crear = False
    abrir_modal_editar = False
    meta_editar_id = None

    # --- 2. Permisos ---
    puede_crear = usuario.role in ["ADMIN", "APOYO"]
    puede_editar = usuario.role in ["ADMIN", "APOYO"]
    puede_eliminar = usuario.role == "ADMIN"

    cfg = ConfiguracionGlobal.objects.first()
    estado_captura = cfg.captura_activa if cfg else True

    if request.method == "POST":
        post_data = request.POST.copy()
        FormClass = MetaFormAdmin

        # --- Activar/Desactivar edición global ---
        if "activar_edicion" in post_data and usuario.role == "ADMIN":
            cfg = ConfiguracionGlobal.objects.first()
            if not cfg:
                cfg = ConfiguracionGlobal.objects.create(captura_activa=True)

            cfg.captura_activa = True
            cfg.save(update_fields=["captura_activa"])
            messages.success(request, "La captura global ha sido ACTIVADA.")
            return redirect("gestion_metas")

        elif "desactivar_edicion" in post_data and usuario.role == "ADMIN":
            cfg = ConfiguracionGlobal.objects.first()
            if not cfg:
                cfg = ConfiguracionGlobal.objects.create(captura_activa=True)

            cfg.captura_activa = False
            cfg.save(update_fields=["captura_activa"])
            messages.success(request, "La captura global ha sido DESACTIVADA.")
            return redirect("gestion_metas")

        # --- Crear meta ---
        if "crear_meta" in post_data and puede_crear:
            form = FormClass(post_data)
            if form.is_valid():
                try:
                    meta = form.save(commit=False)
                    if not meta.clave:
                        meta.clave = "AUTO"
                    meta.save()
                    messages.success(request, "Meta creada correctamente.")
                    return redirect("gestion_metas")
                except Exception as e:
                    messages.error(request, f"Error al crear la meta: {str(e)}")
                    abrir_modal_crear = True
            else:
                abrir_modal_crear = True
                for f, errs in form.errors.items():
                    for err in errs:
                        messages.error(request, f"{f}: {err}")

        # --- Editar meta ---
        elif "editar_meta" in post_data and puede_editar:
            meta_id = post_data.get("meta_id")
            meta = get_object_or_404(Meta, id=meta_id)
            form = FormClass(post_data, instance=meta)
            if form.is_valid():
                try:
                    meta = form.save()
                    messages.success(request, "Meta actualizada correctamente.")
                    return redirect("gestion_metas")
                except Exception as e:
                    messages.error(request, f"Error al actualizar: {e}")
                    abrir_modal_editar = True
                    meta_editar_id = meta_id
            else:
                abrir_modal_editar = True
                meta_editar_id = meta_id

        # --- Eliminar meta ---
        elif "eliminar_meta" in post_data and puede_eliminar:
            meta_id = post_data.get("meta_id")
            meta = get_object_or_404(Meta, id=meta_id)
            try:
                meta.delete()
                messages.success(request, "Meta eliminada correctamente.")
                return redirect("gestion_metas")

            except (ProtectedError, RestrictedError):
                messages.error(
                    request,
                    "No es posible eliminar esta meta porque tiene actividades o avances relacionados.",
                )

            except Exception as e:
                messages.error(request, f"Error inesperado al eliminar: {e}")

    # --- 3. Form por rol ---
    form = MetaFormAdmin() if usuario.role in ["ADMIN", "APOYO"] else MetaFormDocente()
    # --- 5. Generar clave sugerida (para mostrarla en el formulario de creación) ---
    clave = None

    # Solo si hay proyectos disponibles
    proyecto = Proyecto.objects.first()
    if proyecto:
        count = Meta.objects.filter(proyecto=proyecto).count() + 1
        clave = f"{proyecto.clave}-META{count}"

    # --- 4. Render solo con metas ---
    return render(
        request,
        "metas/gestion_metas.html",
        {
            "metas": metas,
            "form": form,
            "estado_captura": estado_captura,
            "abrir_modal_crear": abrir_modal_crear,
            "abrir_modal_editar": abrir_modal_editar,
            "meta_editar_id": meta_editar_id,
            "clave": clave,
            "puede_crear": puede_crear,
            "puede_editar": puede_editar,
            "puede_eliminar": puede_eliminar,
        },
    )


# =============VISTAS PARA EDICION MASIVA=====================
@role_required("ADMIN", "APOYO")
def avance_meta_general_list(request):
    # Ciclo activo desde la sesión
    ciclo_id = request.session.get("ciclo_id")
    ciclo_actual = None
    if ciclo_id:
        ciclo_actual = get_object_or_404(Ciclo, id=ciclo_id)

    # Filtramos los avances solo del ciclo actual de todos los departamentos
    if ciclo_actual:
        avances = (
            AvanceMeta.objects.select_related("metaCumplir", "departamento", "ciclo")
            .filter(ciclo=ciclo_actual)
            .order_by("-fecha_registro")
        )
    else:
        avances = AvanceMeta.objects.none()

    hay_avances = avances.exists()

    departamentos = Departamento.objects.all()
    metas = Meta.objects.select_related("departamento").all().order_by("id")

    avance_form = AvanceMetaGeneralForm()

    # Mapeo de metas con su departamento para JS
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

    # Permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    if request.method == "POST":
        # Crear avance
        if "crear_avance" in request.POST and puede_crear:
            avance_form = AvanceMetaGeneralForm(request.POST)
            if avance_form.is_valid():
                avance = avance_form.save(commit=False)
                avance.ciclo = ciclo_actual  # Se asigna el ciclo actual
                avance.save()
                messages.success(request, "Avance registrado correctamente.")
                return redirect("avance_meta_general_list")
            abrir_modal_avance = True
            messages.error(request, "Error al registrar el avance.")

        # Editar avance
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

        # Eliminar avance
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
            "hay_avances": hay_avances,
            "abrir_modal_avance": abrir_modal_avance,
            "modo_edicion": modo_edicion,
            "avance_id": avance_id,
            "departamentos": departamentos,
            "metas_con_departamentos": json.dumps(metas_con_departamentos),
            "ciclo_actual": ciclo_actual,
        },
    )


# ELIMINAR EN UN FUTURO EN BASE A LA NUEVA LOGICA DE METACICLO YA GUARDA AMBOS VALORES
@role_required("ADMIN", "APOYO")
def meta_comprometida_general_list(request):
    #  Ciclo activo desde la sesión
    ciclo_id = request.session.get("ciclo_id")
    if not ciclo_id:
        messages.error(request, "No hay un ciclo activo seleccionado.")
        return redirect("seleccionar_ciclo")

    ciclo_actual = get_object_or_404(Ciclo, id=ciclo_id)

    # Filtrar metas comprometidas solo del ciclo activo
    comprometidas = (
        MetaComprometida.objects.select_related("meta", "ciclo")
        .filter(ciclo=ciclo_actual)
        .order_by("-id")
    )

    comprometida_form = MetaComprometidaGeneralForm()
    metas_con_comprometida = MetaComprometida.objects.filter(
        ciclo=ciclo_actual
    ).values_list("meta_id", flat=True)

    hay_comprometidas = comprometidas.exists()

    abrir_modal_comprometida = False
    modo_edicion = False
    comprometida_id = None

    # Permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    # Manejo de acciones POST
    if request.method == "POST":
        # --- Crear meta comprometida ---
        if "crear_comprometida" in request.POST and puede_crear:
            comprometida_form = MetaComprometidaGeneralForm(request.POST)
            if comprometida_form.is_valid():
                meta = comprometida_form.cleaned_data["meta"]

                # Evitar duplicados por meta y ciclo
                if MetaComprometida.objects.filter(
                    meta=meta, ciclo=ciclo_actual
                ).exists():
                    messages.error(
                        request,
                        "Ya existe una meta comprometida para esta meta en el ciclo actual.",
                    )
                    abrir_modal_comprometida = True
                else:
                    nueva_comp = comprometida_form.save(commit=False)
                    nueva_comp.ciclo = ciclo_actual
                    nueva_comp.save()
                    messages.success(request, "Meta comprometida creada correctamente.")
                    return redirect("meta_comprometida_general_list")
            else:
                abrir_modal_comprometida = True
                messages.error(request, "Error al crear la meta comprometida.")

        # --- Editar meta comprometida ---
        elif "editar_comprometida" in request.POST and puede_editar:
            comprometida_id = request.POST.get("comprometida_id")
            comp = get_object_or_404(MetaComprometida, id=comprometida_id)
            comprometida_form = MetaComprometidaGeneralForm(request.POST, instance=comp)
            if comprometida_form.is_valid():
                meta = comprometida_form.cleaned_data["meta"]

                # Validar duplicado en ciclo actual
                if (
                    comp.meta != meta
                    and MetaComprometida.objects.filter(
                        meta=meta, ciclo=ciclo_actual
                    ).exists()
                ):
                    messages.error(
                        request,
                        "Ya existe una meta comprometida para esta meta en el ciclo actual.",
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

        # --- Eliminar meta comprometida ---
        elif "eliminar_comprometida" in request.POST and puede_eliminar:
            comprometida_id = request.POST.get("comprometida_id")
            comp = get_object_or_404(MetaComprometida, id=comprometida_id)
            comp.delete()
            messages.success(request, "Meta comprometida eliminada correctamente.")
            return redirect("meta_comprometida_general_list")

        else:
            messages.error(request, "No tienes permiso para realizar esta acción.")

    # Renderizar la plantilla
    return render(
        request,
        "metas/gestion_lista_mComprometida.html",
        {
            "comprometidas": comprometidas,
            "comprometida_form": comprometida_form,
            "hay_comprometidas": hay_comprometidas,
            "abrir_modal_comprometida": abrir_modal_comprometida,
            "modo_edicion": modo_edicion,
            "comprometida_id": comprometida_id,
            "metas_con_comprometida": list(metas_con_comprometida),
            "ciclo_actual": ciclo_actual,
        },
    )


# ====================== VISTAS POR META ======================
@role_required("ADMIN", "APOYO", "DOCENTE")
def gestion_meta_avances(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id)

    # Obtenemos el ciclo activo desde la sesión
    ciclo_id = request.session.get("ciclo_id")
    ciclo_activo = None
    if ciclo_id:
        ciclo_activo = get_object_or_404(Ciclo, id=ciclo_id)
    else:
        messages.warning(request, "No hay un ciclo activo seleccionado.")

    #  Filtramos los avances solo del ciclo activo
    avances = AvanceMeta.objects.filter(metaCumplir=meta, ciclo=ciclo_activo).order_by(
        "-fecha_registro"
    )
    user = request.user
    if user.role == "DOCENTE":
        # El docente solo puede ver avances de su propio departamento
        avances = avances.filter(departamento=user.departamento)

    avance_form = AvanceMetaForm(meta=meta, user=request.user)
    comprometida_form = MetaComprometidaForm()

    abrir_modal_avance = False

    # permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_editar = request.user.role in ["ADMIN", "APOYO", "DOCENTE"]
    puede_eliminar = request.user.role == "ADMIN"

    config = ConfiguracionGlobal.objects.first()
    captura_activa = config.captura_activa if config else True

    if not captura_activa:
        if request.user.role == "DOCENTE":
            puede_crear = False
            puede_editar = False
            puede_eliminar = False

    if request.method == "POST":
        if "crear_avance" in request.POST and puede_crear:
            avance_form = AvanceMetaForm(request.POST, meta=meta, user=request.user)
            if avance_form.is_valid():
                avance = avance_form.save(commit=False)
                avance.metaCumplir = meta
                avance.ciclo = ciclo_activo  #  Vinculamos el ciclo automáticamente
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
            print("ENTRA A EDITAR")
            print(request.POST)

            avance_id = request.POST.get("avance_id")

            avance = get_object_or_404(AvanceMeta, id=avance_id, metaCumplir=meta)

            avance_form = AvanceMetaForm(
                request.POST,
                instance=avance,
                meta=meta,
                user=request.user,
            )

            if avance_form.is_valid():
                avance = avance_form.save(commit=False)

                avance.metaCumplir = meta
                avance.ciclo = ciclo_activo
                avance.departamento = meta.departamento

                avance.save()

                messages.success(request, "Avance actualizado correctamente.")
                return redirect("gestion_meta_avances", meta_id=meta.id)

            abrir_modal_avance = True
            messages.error(request, "Error al editar el avance. Verifique los datos.")

        elif "eliminar_avance" in request.POST and puede_eliminar:
            avance_id = request.POST.get("avance_id")
            avance = get_object_or_404(AvanceMeta, id=avance_id, metaCumplir=meta)
            avance.delete()
            messages.success(request, "Avance eliminado correctamente.")
            return redirect("gestion_meta_avances", meta_id=meta.id)

        else:
            # Si la captura está DESACTIVADA
            if not captura_activa:
                messages.error(
                    request,
                    "El sistema está cerrado. No es posible capturar ni modificar "
                    "información hasta que un administrador lo active.",
                )
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
            "ciclo_activo": ciclo_activo,
        },
    )


# ELIMINAR EN UN FUTURO EN BASE A LA NUEVA LOGICA DE METACICLO YA GUARDA AMBOS VALORES
@role_required("ADMIN", "APOYO")
def gestion_meta_comprometida(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id)
    comprometidas = MetaComprometida.objects.filter(meta=meta).select_related("ciclo")

    comprometida_form = MetaComprometidaForm(initial={"meta": meta})
    abrir_modal = False
    modo_edicion = False

    # Roles
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    # Ciclos disponibles (los que aún no tienen meta comprometida)
    ciclos_asignados = comprometidas.values_list("ciclo_id", flat=True)
    ciclos_disponibles = Ciclo.objects.exclude(id__in=ciclos_asignados)

    if request.method == "POST":
        # CREAR
        if "crear_comprometida" in request.POST and puede_crear:
            form = MetaComprometidaForm(request.POST)
            if form.is_valid():
                meta_instance = form.cleaned_data["meta"]
                ciclo_instance = form.cleaned_data["ciclo"]

                # Evitar duplicados
                if MetaComprometida.objects.filter(
                    meta=meta_instance, ciclo=ciclo_instance
                ).exists():
                    messages.error(
                        request, "Ya existe una meta comprometida para ese ciclo."
                    )
                    abrir_modal = True
                else:
                    form.save()
                    messages.success(request, "Meta comprometida creada correctamente.")
                    return redirect("gestion_meta_comprometida", meta_id=meta.id)
            else:
                abrir_modal = True
                messages.error(request, "Error en el formulario. Verifica los datos.")

        # EDITAR
        elif "editar_comprometida" in request.POST and puede_editar:
            comprometida_id = request.POST.get("comprometida_id")
            comprometida_obj = get_object_or_404(
                MetaComprometida, id=comprometida_id, meta=meta
            )
            form = MetaComprometidaForm(request.POST, instance=comprometida_obj)

            if form.is_valid():
                try:
                    form.save()
                    messages.success(
                        request, "Meta comprometida actualizada correctamente."
                    )
                    return redirect("gestion_meta_comprometida", meta_id=meta.id)
                except IntegrityError:
                    abrir_modal = True
                    modo_edicion = True
                    messages.error(request, "Error al actualizar la meta comprometida.")
            else:
                abrir_modal = True
                modo_edicion = True
                messages.error(request, "Error en el formulario. Verifica los datos.")

        # ELIMINAR
        elif "eliminar_comprometida" in request.POST and puede_eliminar:
            comprometida_id = request.POST.get("comprometida_id")
            comprometida_obj = get_object_or_404(
                MetaComprometida, id=comprometida_id, meta=meta
            )
            comprometida_obj.delete()
            messages.success(request, "Meta comprometida eliminada correctamente.")
            return redirect("gestion_meta_comprometida", meta_id=meta.id)

    return render(
        request,
        "metas/gestion_metaComprometida.html",
        {
            "meta": meta,
            "comprometidas": comprometidas,
            "comprometida_form": comprometida_form,
            "ciclos_disponibles": ciclos_disponibles,
            "abrir_modal": abrir_modal,
            "modo_edicion": modo_edicion,
        },
    )


# ================VISTA PARA TABLA DE SEGUIMIENTO=========================
@role_required("ADMIN", "APOYO", "DOCENTE")
def TablaSeguimiento(request):
    user = request.user

    # 1) Obtener el ciclo
    ciclo_id = request.session.get("ciclo_id")
    ciclo = None
    if ciclo_id:
        ciclo = Ciclo.objects.filter(id=ciclo_id).first()
    if not ciclo:
        ciclo = (
            Ciclo.objects.filter(activo=True).first()
            or Ciclo.objects.order_by("-fecha_inicio").first()
        )

    # 2) Obtener metas según vista y rol
    if request.GET.get("view") == "simple":
        metas_qs = Meta.objects.all().order_by("id")
    else:
        metas_qs = Meta.objects.filter(activa=True).order_by("id")

    if user.role == "ADMIN":
        metas = metas_qs
    elif user.role in ("APOYO", "DOCENTE"):
        metas = metas_qs.filter(departamento=user.departamento)
    else:
        metas = Meta.objects.none()

    # 3) Generar meses
    meses = []
    if ciclo:
        current = ciclo.fecha_inicio.replace(day=1)
        fin = ciclo.fecha_fin
        while current <= fin:
            meses.append(
                {
                    "nombre": current.strftime("%b"),
                    "numero": current.month,
                    "anio": current.year,
                }
            )
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
    else:
        hoy = timezone.now().date().replace(day=1)
        for i in range(11, -1, -1):
            year = hoy.year - ((hoy.month - i - 1) // 12)
            month = ((hoy.month - i - 1) % 12) + 1
            meses.append(
                {
                    "nombre": timezone.datetime(year, month, 1).strftime("%b"),
                    "numero": month,
                    "anio": year,
                }
            )

    # 4) Construir tabla
    tabla = []

    for meta in metas:
        meta_ciclo = MetaCiclo.objects.filter(meta=meta, ciclo=ciclo).first()
        if not meta_ciclo:
            continue

        # Obtener todos los avances asociados a la meta y ciclo
        avances = AvanceMeta.objects.filter(metaCumplir=meta, ciclo=ciclo).order_by(
            "fecha_registro"
        )

        if not avances.exists():
            total = Decimal("0")
        else:
            if meta.acumulable:
                #  Tomar SOLO el último avance registrado
                ultimo_avance = avances.last()
                total = Decimal(str(ultimo_avance.avance or 0))
            else:
                #  Sumar TODOS los avances
                total = avances.aggregate(total=Sum("avance"))["total"] or Decimal("0")

        # Base y meta comprometida
        linea_base = meta_ciclo.lineaBase or Decimal("0")
        meta_cumplir = meta_ciclo.metaCumplir or Decimal("0")

        #  Calcular porcentaje usando la fórmula (B / A) * 100
        porcentaje = Decimal("0")
        try:
            if meta_cumplir != Decimal("0"):
                porcentaje = (total / meta_cumplir) * Decimal("100")
        except (InvalidOperation, TypeError, ZeroDivisionError):
            porcentaje = Decimal("0")

        #  Mostrar valores mensuales (solo referencia visual)
        valores_por_mes = []
        for m in meses:
            year, month = m["anio"], m["numero"]
            avances_mes = avances.filter(
                fecha_registro__year=year, fecha_registro__month=month
            )

            if meta.acumulable:
                # Mostrar solo el último del mes
                av_mes = avances_mes.last()
                valor_mes = av_mes.avance if av_mes else None
            else:
                # Sumar todos los avances del mes
                valor_mes = avances_mes.aggregate(total=Sum("avance"))["total"]

            if not valor_mes or valor_mes == 0:
                valores_por_mes.append("-")
            else:
                val = Decimal(str(valor_mes))
                if meta.porcentages:
                    val = (val * Decimal("100")).quantize(Decimal("0.00"))
                    valores_por_mes.append(f"{val} %")
                else:
                    valores_por_mes.append(f"{val.quantize(Decimal('0.00'))}")

        # 🔹 Formato final
        if meta.porcentages:
            total_display = f"{(total * Decimal('100')).quantize(Decimal('0.00'))} %"
            linea_base_display = (
                f"{(linea_base * Decimal('100')).quantize(Decimal('0.00'))} %"
            )
            meta_cumplir_display = (
                f"{(meta_cumplir * Decimal('100')).quantize(Decimal('0.00'))} %"
            )
        else:
            total_display = f"{total.quantize(Decimal('0.00'))}"
            linea_base_display = f"{linea_base.quantize(Decimal('0.00'))}"
            meta_cumplir_display = f"{meta_cumplir.quantize(Decimal('0.00'))}"

        tabla.append(
            {
                "id": meta.id,
                "meta": meta,
                "clave": meta.clave,
                "meta_nombre": meta.nombre,
                "categoria": "Acumulable" if meta.acumulable else "Incremental",
                "linea_base": linea_base_display,
                "meta_cumplir": meta_cumplir_display,
                "valores_por_mes": valores_por_mes,
                "total": total_display,
                "porcentaje": porcentaje.quantize(Decimal("0.00")),
                "meta_ciclo": meta_ciclo,
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
@role_required("ADMIN", "APOYO", "DOCENTE")
def asignar_ciclo_meta(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id)
    es_docente = request.user.role == "DOCENTE"

    # Configuración para deshabilitar captura a docentes
    puede_editar = True
    config = ConfiguracionGlobal.objects.first()
    captura_activa = config.captura_activa if config else True
    if not captura_activa and es_docente:
        puede_editar = False

    if request.method == "POST":

        # ============================================================
        #         ELIMINAR CICLO
        # ============================================================
        if "eliminar_ciclo" in request.POST:
            meta_ciclo_id = request.POST.get("meta_ciclo_id")
            if meta_ciclo_id:
                try:
                    meta_ciclo = get_object_or_404(
                        MetaCiclo, id=meta_ciclo_id, meta=meta
                    )
                    meta_ciclo.delete()
                    messages.success(request, "Ciclo eliminado correctamente.")
                except Exception as e:
                    messages.error(request, f"Error al eliminar el ciclo: {str(e)}")
            return redirect("asignar_ciclo_meta", meta_id=meta.id)

        # ============================================================
        #         CREAR / EDITAR CICLO
        # ============================================================
        meta_ciclo_id = request.POST.get("meta_ciclo_id")

        if es_docente:
            # DOCENTE -> sin instance, porque no debe tocar ciclo/lineaBase
            form = AsignarCicloMetaForm(request.POST, user=request.user, meta=meta)
        else:
            # ADMIN / APOYO -> usa instance si aplica
            if meta_ciclo_id:
                meta_ciclo_inst = get_object_or_404(
                    MetaCiclo, id=meta_ciclo_id, meta=meta
                )
                form = AsignarCicloMetaForm(
                    request.POST, instance=meta_ciclo_inst, user=request.user, meta=meta
                )
            else:
                form = AsignarCicloMetaForm(request.POST, user=request.user, meta=meta)

        if form.is_valid():

            # ============================================================
            #        DOCENTE — SOLO EDITA metaCumplir
            # ============================================================
            if es_docente and puede_editar:
                if meta_ciclo_id:
                    mc = get_object_or_404(MetaCiclo, id=meta_ciclo_id, meta=meta)

                    meta_cumplir = form.cleaned_data.get("metaCumplir")

                    # Guardar ÚNICAMENTE metaCumplir
                    mc.metaCumplir = meta_cumplir
                    mc.save()

                    messages.success(request, "Meta actualizada correctamente.")

                return redirect("asignar_ciclo_meta", meta_id=meta.id)

            # ============================================================
            #        ADMIN / APOYO — EDITAN TODO
            # ============================================================
            ciclo = form.cleaned_data.get("ciclo")
            linea_base = form.cleaned_data.get("lineaBase")
            meta_cumplir = form.cleaned_data.get("metaCumplir")

            if meta_ciclo_id:
                # EDITAR
                mc = get_object_or_404(MetaCiclo, id=meta_ciclo_id, meta=meta)
                mc.ciclo = ciclo
                mc.lineaBase = linea_base
                mc.metaCumplir = meta_cumplir
                mc.save()
                messages.success(request, "Ciclo actualizado correctamente.")
            else:
                # CREAR — verificar duplicados
                if MetaCiclo.objects.filter(meta=meta, ciclo=ciclo).exists():
                    messages.warning(
                        request, "Ya existe un ciclo asignado para esta meta y ciclo."
                    )
                else:
                    MetaCiclo.objects.create(
                        meta=meta,
                        ciclo=ciclo,
                        lineaBase=linea_base,
                        metaCumplir=meta_cumplir,
                    )
                    messages.success(request, "Ciclo asignado correctamente.")
            return redirect("asignar_ciclo_meta", meta_id=meta.id)

        else:
            messages.error(
                request, "Errores en el formulario: " + form.errors.as_text()
            )

    else:
        # GET
        form = AsignarCicloMetaForm(user=request.user, meta=meta)

    metas_ciclo = MetaCiclo.objects.filter(meta=meta)

    return render(
        request,
        "metas/asignar_ciclo_meta.html",
        {
            "meta": meta,
            "form": form,
            "metas_ciclo": metas_ciclo,
            "es_docente": es_docente,
            "puede_editar": puede_editar,
        },
    )


@role_required("ADMIN", "APOYO")
def asignacion_metas(request):
    """
    Vista para asignar metas a departamentos.
    """
    metas = Meta.objects.filter(activa=True).order_by("clave")
    departamentos = Departamento.objects.all()

    puede_aplicar = request.user.role in ["ADMIN", "APOYO"]

    # --- PETICIÓN AJAX ---
    if (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        and request.method == "POST"
    ):
        data = json.loads(request.body)
        action = data.get("action")

        if action == "apply" and puede_aplicar:
            departamento_id = data.get("departamento")
            meta_ids = data.get("metas", [])

            departamento = None
            if departamento_id:
                try:
                    departamento = Departamento.objects.get(id=departamento_id)
                except Departamento.DoesNotExist:
                    return JsonResponse(
                        {"status": "error", "message": "Departamento no encontrado"}
                    )

            updated_count = 0
            errores = []

            # Usar transacción para asegurar consistencia
            from django.db import transaction

            try:
                with transaction.atomic():
                    for meta_id in meta_ids:
                        try:
                            meta = Meta.objects.get(id=meta_id, activa=True)

                            meta.departamento = departamento
                            meta.save()

                            updated_count += 1

                        except Meta.DoesNotExist:
                            errores.append(f"Meta {meta_id} no encontrada o inactiva")
                        except Exception as e:
                            errores.append(f"Error en meta {meta_id}: {str(e)}")

                return JsonResponse(
                    {
                        "status": "success",
                        "message": f"Se actualizaron {updated_count} metas correctamente",
                        "updated_count": updated_count,
                        "errores": errores,
                        "departamento_asignado": (
                            departamento.nombre if departamento else "Ninguno"
                        ),
                    }
                )

            except Exception as e:
                return JsonResponse(
                    {"status": "error", "message": f"Error en la transacción: {str(e)}"}
                )

        return JsonResponse(
            {
                "status": "error",
                "message": "Acción no permitida o sin permisos",
            }
        )

    # --- PETICIÓN GET NORMAL ---
    context = {
        "metas": metas,
        "departamentos": departamentos,
    }
    return render(request, "metas/asignacion_metas.html", context)


@role_required("ADMIN", "APOYO")
def activar_metas(request):
    if request.method == "POST":

        try:
            # Obtener los datos enviados por el formulario
            meta_ids_raw = request.POST.get("meta_ids")
            action = request.POST.get("accion")

            if not meta_ids_raw:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "No se recibieron metas para procesar.",
                    },
                    status=400,
                )

            meta_ids = json.loads(meta_ids_raw)

            if not isinstance(meta_ids, list) or len(meta_ids) == 0:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "La lista de metas está vacía o es inválida.",
                    },
                    status=400,
                )

            # Validar acción
            if action not in ["activar", "desactivar"]:
                return JsonResponse(
                    {"success": False, "message": "Acción no válida."}, status=400
                )

            # Operación en bloque (todo o nada)
            with transaction.atomic():
                metas = Meta.objects.filter(id__in=meta_ids)

                # Validar que existan las metas
                if not metas.exists():
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "No se encontraron las metas seleccionadas.",
                        },
                        status=404,
                    )
                if action == "desactivar":
                    # Desactivar todas las metas seleccionadas
                    metas.update(activa=False)
                elif action == "activar":  # Activar todas las metas seleccionadas
                    metas.update(activa=True)

            if action == "desactivar":
                mensaje = f"Se desactivaron correctamente {metas.count()} metas."
            else:
                mensaje = f"Se activaron correctamente {metas.count()} metas."

            return JsonResponse({"success": True, "message": mensaje})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    # GET normal → Renderizar página
    metas = Meta.objects.all().order_by("clave")
    return render(request, "metas/activar_metas.html", {"metas": metas})


# =========================API=============================
class MetaViewSet(viewsets.ModelViewSet):
    serializer_class = MetaDetailSerializer

    def get_queryset(self):
        user = self.request.user
        ciclo_id = self.request.query_params.get("ciclo")  # Permitir filtrar por ciclo
        queryset = Meta.objects.all()

        # Si se especifica un ciclo, filtrar metas que tengan datos asociados a ese ciclo
        if ciclo_id:
            queryset = queryset.filter(metaciclo__ciclo_id=ciclo_id).distinct()

        if user.role == "DOCENTE":
            queryset = queryset.filter(departamento=user.departamento)

        elif user.role == "INVITADO":
            queryset = queryset.filter(
                activa=True
            )  # solo metas activas o públicas, si aplica

        return queryset

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


class AvanceMetaViewSet(viewsets.ModelViewSet):
    serializer_class = AvanceMetaSerializer

    def get_queryset(self):
        user = self.request.user
        ciclo_id = self.request.query_params.get("ciclo")

        # Corregido: usar metaCumplir en lugar de meta
        queryset = AvanceMeta.objects.select_related("metaCumplir", "ciclo")

        # Filtrar por ciclo si se indica (muy importante para evitar mezclar años)
        if ciclo_id:
            queryset = queryset.filter(ciclo_id=ciclo_id)

        if user.role in ["ADMIN", "APOYO", "INVITADO"]:
            return queryset
        elif user.role == "DOCENTE":
            return queryset.filter(metaCumplir__departamento=user.departamento)
        return AvanceMeta.objects.none()

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


class MetaComprometidaViewSet(viewsets.ModelViewSet):
    serializer_class = MetaComprometidaSerializer

    def get_queryset(self):
        user = self.request.user
        ciclo_id = self.request.query_params.get("ciclo")
        queryset = MetaComprometida.objects.select_related("meta", "ciclo")

        if ciclo_id:
            queryset = queryset.filter(ciclo_id=ciclo_id)

        if user.role in ["ADMIN", "APOYO"]:
            return queryset
        elif user.role == "DOCENTE":
            return queryset.filter(meta__departamento=user.departamento)
        elif user.role == "INVITADO":
            return queryset  # solo lectura
        return MetaComprometida.objects.none()

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
