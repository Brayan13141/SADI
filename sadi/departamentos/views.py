from rest_framework import viewsets, permissions
from .models import Departamento
from .serializers import DepartamentoSerializer
from django.contrib import messages
from django.shortcuts import get_object_or_404

# ======================CRUD=======================
from django.shortcuts import render, redirect
from .forms import DepartamentoForm


def gestion_departamentos(request):
    departamentos = Departamento.objects.all()
    form = DepartamentoForm()
    abrir_modal_crear = False
    abrir_modal_editar = False

    if request.method == "POST":
        if "crear_departamento" in request.POST:
            form = DepartamentoForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Departamento creado correctamente.")
                return redirect("gestion_departamentos")
            else:
                abrir_modal_crear = True

        elif "editar_departamento" in request.POST:
            departamento_id = request.POST.get("departamento_id")
            departamento = get_object_or_404(Departamento, id=departamento_id)
            form = DepartamentoForm(request.POST, instance=departamento)
            if form.is_valid():
                form.save()
                messages.success(request, "Departamento editado correctamente.")
                return redirect("gestion_departamentos")
            else:
                abrir_modal_editar = True

        elif "eliminar_departamento" in request.POST:
            departamento_id = request.POST.get("departamento_id")
            departamento = get_object_or_404(Departamento, id=departamento_id)
            departamento.delete()
            messages.success(request, "Departamento eliminado correctamente.")
            return redirect("gestion_departamentos")

    return render(
        request,
        "departamentos/gestion_departamentos.html",
        {
            "departamentos": departamentos,
            "form": form,
            "abrir_modal_crear": abrir_modal_crear,
            "abrir_modal_editar": abrir_modal_editar,
        },
    )


# ========================API=======================
class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [permissions.IsAuthenticated]
