from rest_framework import viewsets, permissions
from .models import ProgramaEstrategico, Ciclo
from .serializers import ProgramaEstrategicoSerializer, CicloSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProgramaEstrategicoForm, CicloForm


def gestion_programas(request):
    programas = ProgramaEstrategico.objects.all()
    form_crear = ProgramaEstrategicoForm()
    abrir_modal_crear = False
    abrir_modal_editar = False
    programa_editar_id = None

    if request.method == "POST":
        if "crear_programa" in request.POST:
            form_crear = ProgramaEstrategicoForm(request.POST)
            if form_crear.is_valid():
                form_crear.save()
                return redirect("gestion_programas")
            else:
                abrir_modal_crear = True

        elif "editar_programa" in request.POST:
            programa_id = request.POST.get("programa_id")
            if programa_id:  # Validación importante
                try:
                    programa = get_object_or_404(ProgramaEstrategico, id=programa_id)
                    form_editar = ProgramaEstrategicoForm(
                        request.POST, instance=programa
                    )
                    if form_editar.is_valid():
                        form_editar.save()
                        return redirect("gestion_programas")
                    else:
                        # Guardar el ID para pre-cargar el form en el template
                        programa_editar_id = programa_id
                        abrir_modal_editar = True
                except (ValueError, ProgramaEstrategico.DoesNotExist):
                    # Manejar error aquí si es necesario
                    pass
            else:
                # Manejar el caso cuando programa_id está vacío
                pass

        elif "eliminar_programa" in request.POST:
            programa_id = request.POST.get("programa_id")
            if programa_id:  # Validación importante
                programa = get_object_or_404(ProgramaEstrategico, id=programa_id)
                programa.delete()
            return redirect("gestion_programas")

    # Crear form de edición si hay un programa específico para editar
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
        },
    )


# Vistas para Ciclo
def gestion_ciclos(request):
    ciclos = Ciclo.objects.all().select_related("programa")
    form = CicloForm()

    if request.method == "POST":
        if "crear_ciclo" in request.POST:
            form = CicloForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("gestion_ciclos")
        elif "editar_ciclo" in request.POST:
            ciclo_id = request.POST.get("ciclo_id")
            ciclo = get_object_or_404(Ciclo, id=ciclo_id)
            form = CicloForm(request.POST, instance=ciclo)
            if form.is_valid():
                form.save()
                return redirect("gestion_ciclos")
        elif "eliminar_ciclo" in request.POST:
            ciclo_id = request.POST.get("ciclo_id")
            ciclo = get_object_or_404(Ciclo, id=ciclo_id)
            ciclo.delete()
            return redirect("gestion_ciclos")

    return render(
        request, "programas/gestion_ciclos.html", {"ciclos": ciclos, "form": form}
    )


# ========================API========================
class ProgramaEstrategicoViewSet(viewsets.ModelViewSet):
    queryset = ProgramaEstrategico.objects.all()
    serializer_class = ProgramaEstrategicoSerializer
    permission_classes = [permissions.IsAuthenticated]


class CicloViewSet(viewsets.ModelViewSet):
    queryset = Ciclo.objects.all()
    serializer_class = CicloSerializer
    permission_classes = [permissions.IsAuthenticated]
