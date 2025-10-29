from rest_framework import viewsets, permissions

from programas.serializers import CicloSerializer
from usuarios.permissions import IsAdmin, IsApoyo, IsDocente, IsInvitado
from .models import ObjetivoEstrategico
from .serializers import ObjetivoEstrategicoSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ObjetivoEstrategicoForm
from django.contrib import messages
from usuarios.decorators import role_required


@role_required("ADMIN", "APOYO")
def gestion_objetivos(request):
    objetivos = ObjetivoEstrategico.objects.all().select_related("programa")
    form_crear = ObjetivoEstrategicoForm()
    abrir_modal_crear = False
    abrir_modal_editar = False
    objetivo_editar_id = None

    # permisos por rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    if request.method == "POST":
        if "crear_objetivo" in request.POST and puede_crear:
            form_crear = ObjetivoEstrategicoForm(request.POST)
            if form_crear.is_valid():
                form_crear.save()
                messages.success(request, "Objetivo creado correctamente.")
                return redirect("gestion_objetivos")
            abrir_modal_crear = True
            for field, errors in form_crear.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        elif "editar_objetivo" in request.POST and puede_editar:
            objetivo_id = request.POST.get("objetivo_id")
            if objetivo_id:
                try:
                    objetivo = get_object_or_404(ObjetivoEstrategico, id=objetivo_id)
                    form_editar = ObjetivoEstrategicoForm(
                        request.POST, instance=objetivo
                    )
                    if form_editar.is_valid():
                        form_editar.save()
                        messages.success(request, "Objetivo editado correctamente.")
                        return redirect("gestion_objetivos")
                    objetivo_editar_id = objetivo_id
                    abrir_modal_editar = True
                    for field, errors in form_editar.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                except Exception as e:
                    messages.error(request, f"Error al editar: {str(e)}")

        elif "eliminar_objetivo" in request.POST and puede_eliminar:
            objetivo_id = request.POST.get("objetivo_id")
            if objetivo_id:
                objetivo = get_object_or_404(ObjetivoEstrategico, id=objetivo_id)
                objetivo.delete()
                messages.success(request, "Objetivo eliminado correctamente.")
            return redirect("gestion_objetivos")

    # Crear form de edición si hay un objetivo específico para editar
    form_editar = None
    if objetivo_editar_id:
        objetivo = get_object_or_404(ObjetivoEstrategico, id=objetivo_editar_id)
        form_editar = ObjetivoEstrategicoForm(instance=objetivo)

    return render(
        request,
        "objetivos/gestion_objetivos.html",
        {
            "objetivos": objetivos,
            "form_crear": form_crear,
            "form_editar": form_editar,
            "abrir_modal_crear": abrir_modal_crear,
            "abrir_modal_editar": abrir_modal_editar,
            "objetivo_editar_id": objetivo_editar_id,
        },
    )


# ===========================API========================================
class ObjetivoEstrategicoViewSet(viewsets.ModelViewSet):
    serializer_class = ObjetivoEstrategicoSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "APOYO", "INVITADO"]:
            return ObjetivoEstrategico.objects.all()
        elif user.role == "DOCENTE":
            return ObjetivoEstrategico.objects.filter(
                proyecto__departamento=user.departamento
            )
        return ObjetivoEstrategico.objects.none()

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
