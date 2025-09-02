from rest_framework import viewsets, permissions
from .models import Riesgo, Mitigacion
from .serializers import RiesgoSerializer, MitigacionSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Riesgo, Mitigacion
from .forms import RiesgoForm, MitigacionForm


def gestion_riesgos(request):
    riesgos = Riesgo.objects.all().select_related("meta")
    form = RiesgoForm()

    if request.method == "POST":
        if "crear_riesgo" in request.POST:
            form = RiesgoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("gestion_riesgos")
        elif "editar_riesgo" in request.POST:
            riesgo_id = request.POST.get("riesgo_id")
            riesgo = get_object_or_404(Riesgo, id=riesgo_id)
            form = RiesgoForm(request.POST, instance=riesgo)
            if form.is_valid():
                form.save()
                return redirect("gestion_riesgos")
        elif "eliminar_riesgo" in request.POST:
            riesgo_id = request.POST.get("riesgo_id")
            riesgo = get_object_or_404(Riesgo, id=riesgo_id)
            riesgo.delete()
            return redirect("gestion_riesgos")

    return render(
        request, "riesgos/gestion_riesgos.html", {"riesgos": riesgos, "form": form}
    )


# Vistas para Mitigacion
def gestion_mitigaciones(request):
    mitigaciones = Mitigacion.objects.all().select_related("responsable", "riesgo")
    form = MitigacionForm()

    if request.method == "POST":
        if "crear_mitigacion" in request.POST:
            form = MitigacionForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("gestion_mitigaciones")
        elif "editar_mitigacion" in request.POST:
            mitigacion_id = request.POST.get("mitigacion_id")
            mitigacion = get_object_or_404(Mitigacion, id=mitigacion_id)
            form = MitigacionForm(request.POST, instance=mitigacion)
            if form.is_valid():
                form.save()
                return redirect("gestion_mitigaciones")
        elif "eliminar_mitigacion" in request.POST:
            mitigacion_id = request.POST.get("mitigacion_id")
            mitigacion = get_object_or_404(Mitigacion, id=mitigacion_id)
            mitigacion.delete()
            return redirect("gestion_mitigaciones")

    return render(
        request,
        "riesgos/gestion_mitigaciones.html",
        {"mitigaciones": mitigaciones, "form": form},
    )


# ===================API===================
class RiesgoViewSet(viewsets.ModelViewSet):
    queryset = Riesgo.objects.all()
    serializer_class = RiesgoSerializer
    permission_classes = [permissions.IsAuthenticated]


class MitigacionViewSet(viewsets.ModelViewSet):
    queryset = Mitigacion.objects.all()
    serializer_class = MitigacionSerializer
    permission_classes = [permissions.IsAuthenticated]
