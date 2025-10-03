from rest_framework import viewsets, permissions
from .models import ProgramaEstrategico, Ciclo
from .serializers import CicloSerializer, ProgramaEstrategicoSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProgramaEstrategicoForm, CicloForm
from django.contrib import messages
from usuarios.permissions import IsAdmin, IsApoyo, IsDocente, IsInvitado
from usuarios.decorators import role_required
from rest_framework.exceptions import PermissionDenied


@role_required("ADMIN", "APOYO")
def gestion_programas(request):
    programas = ProgramaEstrategico.objects.all()
    form_crear = ProgramaEstrategicoForm()
    abrir_modal_crear = False
    abrir_modal_editar = False
    programa_editar_id = None

    # permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    if request.method == "POST":
        if "crear_programa" in request.POST and puede_crear:
            form_crear = ProgramaEstrategicoForm(request.POST)
            if form_crear.is_valid():
                form_crear.save()
                messages.success(request, "Programa creado exitosamente.")
                return redirect("gestion_programas")
            abrir_modal_crear = True

        elif "editar_programa" in request.POST and puede_editar:
            programa_id = request.POST.get("programa_id")
            if programa_id:
                programa = get_object_or_404(ProgramaEstrategico, id=programa_id)
                form_editar = ProgramaEstrategicoForm(request.POST, instance=programa)
                if form_editar.is_valid():
                    form_editar.save()
                    messages.success(request, "Programa actualizado exitosamente.")
                    return redirect("gestion_programas")
                abrir_modal_editar = True
                programa_editar_id = programa_id

        elif "eliminar_programa" in request.POST and puede_eliminar:
            programa_id = request.POST.get("programa_id")
            if programa_id:
                programa = get_object_or_404(ProgramaEstrategico, id=programa_id)
                programa.delete()
                messages.success(request, "Programa eliminado exitosamente.")
            return redirect("gestion_programas")

    form_editar = None
    if programa_editar_id:
        programa = get_object_or_404(ProgramaEstrategico, id=programa_editar_id)
        form_editar = ProgramaEstrategicoForm(instance=programa)

    return render(
        request,
        "programas/gestion_programas.html",
        {
            "programas": programas,
            "form_crear": form_crear,
            "form_editar": form_editar,
            "abrir_modal_crear": abrir_modal_crear,
            "abrir_modal_editar": abrir_modal_editar,
            "programa_editar_id": programa_editar_id,
            "puede_crear": puede_crear,
            "puede_editar": puede_editar,
            "puede_eliminar": puede_eliminar,
        },
    )


@role_required("ADMIN", "APOYO")
def gestion_ciclos(request):
    ciclos = Ciclo.objects.all().select_related("programa")
    form = CicloForm()
    abrir_modal_crear = False
    abrir_modal_editar = False

    # permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    if request.method == "POST":
        if "crear_ciclo" in request.POST and puede_crear:
            form = CicloForm(request.POST)
            if form.is_valid():
                ciclo = form.save(commit=False)
                ciclo.save()  # calcula duración en el save()
                messages.success(request, "Ciclo creado exitosamente.")
                return redirect("gestion_ciclos")
            abrir_modal_crear = True

        elif "editar_ciclo" in request.POST and puede_editar:
            ciclo_id = request.POST.get("ciclo_id")
            ciclo = get_object_or_404(Ciclo, id=ciclo_id)
            form = CicloForm(request.POST, instance=ciclo)
            if form.is_valid():
                ciclo = form.save(commit=False)
                ciclo.save()
                messages.success(request, "Ciclo actualizado exitosamente.")
                return redirect("gestion_ciclos")
            abrir_modal_editar = True
            request.session["ciclo_editar_id"] = ciclo_id

        elif "eliminar_ciclo" in request.POST and puede_eliminar:
            ciclo_id = request.POST.get("ciclo_id")
            ciclo = get_object_or_404(Ciclo, id=ciclo_id)
            ciclo.delete()
            messages.success(request, "Ciclo eliminado exitosamente.")
            return redirect("gestion_ciclos")

    form_editar = None
    ciclo_editar_id = request.session.get("ciclo_editar_id")
    if ciclo_editar_id:
        ciclo = get_object_or_404(Ciclo, id=ciclo_editar_id)
        form_editar = CicloForm(instance=ciclo)
        request.session.pop("ciclo_editar_id", None)

    return render(
        request,
        "programas/gestion_ciclos.html",
        {
            "ciclos": ciclos,
            "form": form,
            "form_editar": form_editar,
            "abrir_modal_crear": abrir_modal_crear,
            "abrir_modal_editar": abrir_modal_editar,
        },
    )


# ========================API========================


class ProgramaEstrategicoViewSet(viewsets.ModelViewSet):
    serializer_class = ProgramaEstrategicoSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role in ["ADMIN", "APOYO", "INVITADO"]:
            return ProgramaEstrategico.objects.all()

        elif user.role == "DOCENTE":
            return ProgramaEstrategico.objects.filter(
                objetivos__proyecto__meta__departamento=user.departamento
            ).distinct()

        return ProgramaEstrategico.objects.none()

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.role == "DOCENTE":
            if not ProgramaEstrategico.objects.filter(
                id=obj.id,
                objetivos__proyecto__meta__departamento=user.departamento,
            ).exists():
                raise PermissionDenied("No tienes acceso a este programa.")
        return obj


class CicloViewSet(viewsets.ModelViewSet):
    serializer_class = CicloSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "APOYO", "INVITADO"]:
            return Ciclo.objects.all()
        elif user.role == "DOCENTE":
            return Ciclo.objects.filter(
                objetivos__proyecto__departamento=user.departamento
            ).distinct()
        return Ciclo.objects.none()

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
