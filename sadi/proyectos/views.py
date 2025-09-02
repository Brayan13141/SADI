from rest_framework import viewsets, permissions
from .models import Proyecto
from .serializers import ProyectoSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import ProyectoForm


def gestion_proyectos(request):
    proyectos = Proyecto.objects.all().select_related("objetivo")
    form = ProyectoForm()

    if request.method == "POST":
        if "crear_proyecto" in request.POST:
            form = ProyectoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("gestion_proyectos")
        elif "editar_proyecto" in request.POST:
            proyecto_id = request.POST.get("proyecto_id")
            proyecto = get_object_or_404(Proyecto, id=proyecto_id)
            form = ProyectoForm(request.POST, instance=proyecto)
            if form.is_valid():
                form.save()
                return redirect("gestion_proyectos")
        elif "eliminar_proyecto" in request.POST:
            proyecto_id = request.POST.get("proyecto_id")
            proyecto = get_object_or_404(Proyecto, id=proyecto_id)
            proyecto.delete()
            return redirect("gestion_proyectos")

    return render(
        request,
        "proyectos/gestion_proyectos.html",
        {"proyectos": proyectos, "form": form},
    )


# ====================API=================
class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [permissions.IsAuthenticated]
