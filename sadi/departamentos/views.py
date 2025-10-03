from rest_framework import viewsets, permissions
from .models import Departamento
from .serializers import DepartamentoSerializer
from django.contrib import messages
from django.shortcuts import get_object_or_404
from usuarios.permissions import IsAdmin, IsApoyo, IsDocente
from usuarios.decorators import role_required

# ======================CRUD=======================
from django.shortcuts import render, redirect
from .forms import DepartamentoForm


@role_required("ADMIN", "APOYO")
def gestion_departamentos(request):
    departamentos = Departamento.objects.all()
    form = DepartamentoForm()
    abrir_modal_crear = False
    abrir_modal_editar = False
    # permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    if request.method == "POST":
        if "crear_departamento" in request.POST and puede_crear:
            form = DepartamentoForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Departamento creado correctamente.")
                return redirect("gestion_departamentos")
            abrir_modal_crear = True

        elif "editar_departamento" in request.POST and puede_editar:
            departamento_id = request.POST.get("departamento_id")
            departamento = get_object_or_404(Departamento, id=departamento_id)
            form = DepartamentoForm(request.POST, instance=departamento)
            if form.is_valid():
                form.save()
                messages.success(request, "Departamento editado correctamente.")
                return redirect("gestion_departamentos")
            abrir_modal_editar = True

        elif "eliminar_departamento" in request.POST and puede_eliminar:
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

from .filters import DepartamentoFilter
from django_filters.rest_framework import DjangoFilterBackend


class DepartamentoViewSet(viewsets.ModelViewSet):
    serializer_class = DepartamentoSerializer
    queryset = Departamento.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = DepartamentoFilter

    def get_permissions(self):
        if self.request.user.role == "ADMIN":
            return [IsAdmin()]
        elif self.request.user.role == "APOYO":
            return [IsApoyo()]
        elif self.request.user.role == "DOCENTE":
            return [IsDocente()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if user.role in ["ADMIN", "APOYO"]:
            return queryset
        elif user.role == "DOCENTE":
            return queryset.filter(id=user.departamento_id)
        return Departamento.objects.none()
