from rest_framework import viewsets, permissions
from .models import Actividad
from django.contrib.auth.decorators import login_required
from metas.models import Meta
from .serializers import ActividadSerializer
from django.shortcuts import render, redirect, get_object_or_404
from usuarios.models import Usuario
from .forms import ActividadForm


# =====================CRUD=====================
def gestion_actividades(request):
    actividades = Actividad.objects.all().select_related("meta", "responsable")
    form = ActividadForm()

    if request.method == "POST":
        if "crear_actividad" in request.POST:
            form = ActividadForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("gestion_actividades")
        elif "editar_actividad" in request.POST:
            actividad_id = request.POST.get("actividad_id")
            actividad = get_object_or_404(Actividad, id=actividad_id)
            form = ActividadForm(request.POST, instance=actividad)
            if form.is_valid():
                form.save()
                return redirect("gestion_actividades")
        elif "eliminar_actividad" in request.POST:
            actividad_id = request.POST.get("actividad_id")
            actividad = get_object_or_404(Actividad, id=actividad_id)
            actividad.delete()
            return redirect("gestion_actividades")

    return render(
        request,
        "actividades/gestion_actividades.html",
        {"actividades": actividades, "form": form},
    )


# =========================VISTAS=================================


def ver_actividades(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id)
    actividades = Actividad.objects.filter(meta=meta)
    return render(
        request,
        "actividades/ver_actividades.html",
        {
            "meta": meta,
            "actividades": actividades,
        },
    )


def agregar_actividad(request, meta_id):
    meta = get_object_or_404(Meta, id=meta_id)
    usuarios = Usuario.objects.all()  # 👉 para llenar el select

    if request.method == "POST":
        descripcion = request.POST.get("descripcion")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")
        responsable_id = request.POST.get("responsable")
        evidencia = request.POST.get("evidencia")

        if responsable_id:  # validar que se seleccionó un usuario
            responsable = Usuario.objects.get(id=responsable_id)
            Actividad.objects.create(
                descripcion=descripcion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                evidencia=evidencia,
                responsable=responsable,
                meta=meta,
            )
            return redirect("ver_actividades", meta_id=meta.id)

    return render(
        request,
        "actividades/agregar_actividad.html",
        {"meta": meta, "usuarios": usuarios},
    )


# ===============================API===============================
class ActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = [permissions.IsAuthenticated]
