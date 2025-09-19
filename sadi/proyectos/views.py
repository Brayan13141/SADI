from django.contrib import messages
from rest_framework import viewsets, permissions
from usuarios.decorators import role_required
from usuarios.permissions import IsAdmin, IsApoyo, IsDocente, IsInvitado
from .models import Proyecto
from .serializers import ProyectoSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProyectoForm


@role_required("ADMIN", "APOYO")
def gestion_proyectos(request):
    proyectos = Proyecto.objects.all().select_related("objetivo")
    form = ProyectoForm()
    abrir_modal_crear = False
    abrir_modal_editar = False
    proyecto_editar_id = None

    # permisos según rol
    puede_crear = request.user.role in ["ADMIN", "APOYO"]
    puede_editar = request.user.role in ["ADMIN", "APOYO"]
    puede_eliminar = request.user.role == "ADMIN"

    if request.method == "POST":
        if "crear_proyecto" in request.POST and puede_crear:
            form = ProyectoForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Proyecto creado correctamente.")
                return redirect("gestion_proyectos")
            abrir_modal_crear = True
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, "Vuelve a intentarlo")

        elif "editar_proyecto" in request.POST and puede_editar:
            proyecto_id = request.POST.get("proyecto_id")
            if proyecto_id:
                try:
                    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
                    form = ProyectoForm(request.POST, instance=proyecto)
                    if form.is_valid():
                        form.save()
                        messages.success(request, "Proyecto editado correctamente.")
                        return redirect("gestion_proyectos")
                    proyecto_editar_id = proyecto_id
                    abrir_modal_editar = True
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"{field}: {error}")
                except Exception:
                    messages.error(request, "Vuelve a intentarlo")

        elif "eliminar_proyecto" in request.POST and puede_eliminar:
            proyecto_id = request.POST.get("proyecto_id")
            if proyecto_id:
                proyecto = get_object_or_404(Proyecto, id=proyecto_id)
                proyecto.delete()
                messages.success(request, "Proyecto eliminado correctamente.")
            return redirect("gestion_proyectos")

    return render(
        request,
        "proyectos/gestion_proyectos.html",
        {
            "proyectos": proyectos,
            "form": form,
            "abrir_modal_crear": abrir_modal_crear,
            "abrir_modal_editar": abrir_modal_editar,
            "proyecto_editar_id": proyecto_editar_id,
        },
    )


# ====================API=================
class ProyectoViewSet(viewsets.ModelViewSet):
    serializer_class = ProyectoSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "APOYO", "INVITADO"]:
            return Proyecto.objects.all()
        elif user.role == "DOCENTE":
            return Proyecto.objects.filter(
                objetivo__programa__ciclos__objetivos__proyecto__departamento=user.departamento
            ).distinct()
        return Proyecto.objects.none()

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
