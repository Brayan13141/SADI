from rest_framework import viewsets, permissions
from .models import ObjetivoEstrategico
from .serializers import ObjetivoEstrategicoSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ObjetivoEstrategicoForm
from django.http import JsonResponse


# Vistas para ObjetivoEstrategico
def gestion_objetivos(request):
    objetivos = ObjetivoEstrategico.objects.all().select_related("ciclo", "programa")
    form = ObjetivoEstrategicoForm()

    if request.method == "POST":
        if "crear_objetivo" in request.POST:
            form = ObjetivoEstrategicoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("gestion_objetivos")
        elif "editar_objetivo" in request.POST:
            objetivo_id = request.POST.get("objetivo_id")
            objetivo = get_object_or_404(ObjetivoEstrategico, id=objetivo_id)
            form = ObjetivoEstrategicoForm(request.POST, instance=objetivo)
            if form.is_valid():
                form.save()
                return redirect("gestion_objetivos")
        elif "eliminar_objetivo" in request.POST:
            objetivo_id = request.POST.get("objetivo_id")
            objetivo = get_object_or_404(ObjetivoEstrategico, id=objetivo_id)
            objetivo.delete()
            return redirect("gestion_objetivos")

    return render(
        request,
        "objetivos/gestion_objetivos.html",
        {"objetivos": objetivos, "form": form},
    )


def objetivo_json(request, objetivo_id):
    objetivo = get_object_or_404(ObjetivoEstrategico, id=objetivo_id)
    data = {
        "id": objetivo.id,
        "descripcion": objetivo.descripcion,
        "ciclo_id": objetivo.ciclo.id,
        "programa_id": objetivo.programa.id,
    }
    return JsonResponse(data)


# ===========================API======================
class ObjetivoEstrategicoViewSet(viewsets.ModelViewSet):
    queryset = ObjetivoEstrategico.objects.all()
    serializer_class = ObjetivoEstrategicoSerializer
    permission_classes = [permissions.IsAuthenticated]
