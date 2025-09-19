from django.shortcuts import redirect, render, get_object_or_404
from rest_framework import viewsets, permissions
from actividades.models import Actividad
from .models import Meta, AvanceMeta, MetaComprometida
from django.contrib.auth.decorators import login_required
from programas.models import Ciclo
from django.db.models import Sum
from django.utils import timezone

from .serializers import (
    MetaSerializer,
    AvanceMetaSerializer,
    MetaComprometidaSerializer,
)

# ==============CRUD=======================
from django.http import JsonResponse
from .forms import MetaForm, AvanceMetaForm, MetaComprometidaForm


def gestion_metas(request):
    metas = Meta.objects.all().select_related("proyecto", "departamento")
    form = MetaForm()

    if request.method == "POST":
        if "crear_meta" in request.POST:
            form = MetaForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("gestion_metas")
        elif "editar_meta" in request.POST:
            meta_id = request.POST.get("meta_id")
            meta = get_object_or_404(Meta, id=meta_id)
            form = MetaForm(request.POST, instance=meta)
            if form.is_valid():
                form.save()
                return redirect("gestion_metas")
        elif "eliminar_meta" in request.POST:
            meta_id = request.POST.get("meta_id")
            meta = get_object_or_404(Meta, id=meta_id)
            meta.delete()
            return redirect("gestion_metas")

    return render(request, "metas/gestion_metas.html", {"metas": metas, "form": form})


def meta_json(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id)
    data = {
        "id": meta.id,
        "nombre": meta.nombre,
        "clave": meta.clave,
        "enunciado": meta.enunciado,
        "proyecto_id": meta.proyecto.id,
        "departamento_id": meta.departamento.id if meta.departamento else None,
        "indicador": meta.indicador,
        "unidadMedida": meta.unidadMedida,
        "porcentages": meta.porcentages,
        "activa": meta.activa,
        "metodoCalculo": meta.metodoCalculo,
        "lineabase": str(meta.lineabase) if meta.lineabase else None,
        "metacumplir": str(meta.metacumplir) if meta.metacumplir else None,
        "variableB": str(meta.variableB) if meta.variableB else None,
    }
    return JsonResponse(data)


# Vistas para AvanceMeta
def gestion_avances_meta(request):
    avances = AvanceMeta.objects.all().select_related("metaCumplir", "departamento")
    form = AvanceMetaForm()

    if request.method == "POST":
        if "crear_avance" in request.POST:
            form = AvanceMetaForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("gestion_avances_meta")
        elif "editar_avance" in request.POST:
            avance_id = request.POST.get("avance_id")
            avance = get_object_or_404(AvanceMeta, id=avance_id)
            form = AvanceMetaForm(request.POST, instance=avance)
            if form.is_valid():
                form.save()
                return redirect("gestion_avances_meta")
        elif "eliminar_avance" in request.POST:
            avance_id = request.POST.get("avance_id")
            avance = get_object_or_404(AvanceMeta, id=avance_id)
            avance.delete()
            return redirect("gestion_avances_meta")

    return render(
        request, "metas/gestion_avances_meta.html", {"avances": avances, "form": form}
    )


# Vistas para MetaComprometida
def gestion_metas_comprometidas(request):
    metas_comprometidas = MetaComprometida.objects.all().select_related(
        "meta", "programa"
    )
    form = MetaComprometidaForm()

    if request.method == "POST":
        if "crear_meta_comprometida" in request.POST:
            form = MetaComprometidaForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("gestion_metas_comprometidas")
        elif "editar_meta_comprometida" in request.POST:
            meta_comprometida_id = request.POST.get("meta_comprometida_id")
            meta_comprometida = get_object_or_404(
                MetaComprometida, id=meta_comprometida_id
            )
            form = MetaComprometidaForm(request.POST, instance=meta_comprometida)
            if form.is_valid():
                form.save()
                return redirect("gestion_metas_comprometidas")
        elif "eliminar_meta_comprometida" in request.POST:
            meta_comprometida_id = request.POST.get("meta_comprometida_id")
            meta_comprometida = get_object_or_404(
                MetaComprometida, id=meta_comprometida_id
            )
            meta_comprometida.delete()
            return redirect("gestion_metas_comprometidas")

    return render(
        request,
        "metas/gestion_metas_comprometidas.html",
        {"metas_comprometidas": metas_comprometidas, "form": form},
    )


# =============VISTAS=====================


@login_required
def TablaSeguimiento(request):
    # Obtener el ciclo activo o el más reciente
    try:
        ciclo = Ciclo.objects.filter(activo=True).first()
        if not ciclo:
            ciclo = Ciclo.objects.order_by("-fecha_inicio").first()
    except Ciclo.DoesNotExist:
        ciclo = None

    # Obtener todas las metas y ordenarlas
    metas = Meta.objects.all().order_by("id")
    tabla = []

    # Obtener meses para el ciclo actual o usar meses por defecto
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
            # Avanzar al siguiente mes
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    else:
        # Si no hay ciclo, usar los últimos 12 meses
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

    # Calcular datos para cada meta
    for meta in metas:
        # Obtener avances para esta meta
        avances = AvanceMeta.objects.filter(metaCumplir=meta)

        # Calcular total acumulado
        total = avances.aggregate(total=Sum("avance"))["total"] or 0

        # Calcular porcentaje de avance
        if meta.metacumplir > 0:
            porcentaje = min(100, (total / meta.metacumplir) * 100)
        else:
            porcentaje = 0

        # Crear lista ordenada de valores por mes
        valores_por_mes = []
        for mes_info in meses:
            # Buscar si hay avance para este mes específico
            avance_mes = None
            for avance in avances:
                if (
                    avance.fecha_registro.year == mes_info["anio"]
                    and avance.fecha_registro.month == mes_info["numero"]
                ):
                    avance_mes = avance.avance
                    break

            valores_por_mes.append(avance_mes)

        # Obtener actividades relacionadas
        actividades = meta.actividad_set.all()

        tabla.append(
            {
                "id": meta.id,
                "meta": meta,
                "valores_por_mes": valores_por_mes,  # Lista ordenada de valores
                "total": total,
                "porcentaje": round(porcentaje, 1),
                "actividades": actividades,
            }
        )

    # Calcular avance promedio
    if tabla:
        avance_promedio = sum(item["porcentaje"] for item in tabla) / len(tabla)
    else:
        avance_promedio = 0

    context = {
        "tabla": tabla,
        "ciclo": ciclo,
        "meses": meses,
        "avance_promedio": round(avance_promedio, 1),
    }

    return render(request, "metas/tablaSeguimiento.html", context)


# =========================API=============================
class MetaViewSet(viewsets.ModelViewSet):
    queryset = Meta.objects.all()
    serializer_class = MetaSerializer
    permission_classes = [permissions.IsAuthenticated]


class AvanceMetaViewSet(viewsets.ModelViewSet):
    queryset = AvanceMeta.objects.all()
    serializer_class = AvanceMetaSerializer
    permission_classes = [permissions.IsAuthenticated]


class MetaComprometidaViewSet(viewsets.ModelViewSet):
    queryset = MetaComprometida.objects.all()
    serializer_class = MetaComprometidaSerializer
    permission_classes = [permissions.IsAuthenticated]
