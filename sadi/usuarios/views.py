from .models import Usuario
from rest_framework import viewsets, permissions
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import UsuarioEditForm, UsuarioForm
from .serializers import UsuarioSerializer
from .decorators import role_required


@role_required("ADMIN")
def gestion_usuarios(request):
    usuarios = Usuario.objects.all()
    form = UsuarioForm()
    form_edit = UsuarioEditForm()
    abrir_modal_crear = False

    if request.method == "POST":
        if "crear_usuario" in request.POST:
            form = UsuarioForm(request.POST)

            if form.is_valid():
                usuario = form.save()
                messages.success(request, "Usuario creado correctamente.")
                return redirect("gestion_usuarios")
            else:
                abrir_modal_crear = True
                messages.error(
                    request,
                    form.errors,
                )
                return redirect("gestion_usuarios")

        elif "editar_usuario" in request.POST:
            usuario_id = request.POST.get("usuario_id")
            usuario = get_object_or_404(Usuario, id=usuario_id)
            form = UsuarioEditForm(request.POST, instance=usuario)

            if form.is_valid():
                form.save()
                messages.success(request, "Usuario editado correctamente.")
                return redirect("gestion_usuarios")
            else:
                messages.error(
                    request,
                    form.errors,
                )
        elif "desactivar_user" in request.POST:
            usuario_id = request.POST.get("usuario_id")
            usuario = get_object_or_404(Usuario, id=usuario_id)
            usuario.is_active = False
            usuario.save()
            messages.success(request, "Usuario desactivado correctamente.")
            return redirect("gestion_usuarios")

    return render(
        request,
        "usuarios/gestion_usuarios.html",
        {
            "usuarios": usuarios,
            "form": form,
            "abrir_modal_crear": abrir_modal_crear,
            "form_edit": form_edit,
        },
    )


class UsuarioViewSet(viewsets.ModelViewSet):

    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.request.user.role == "ADMIN":
            return [permissions.IsAuthenticated()]  # Admin puede todo
        else:
            return [permissions.IsAuthenticatedOrReadOnly()]  # Lectura para otros roles

    def get_queryset(self):
        user = self.request.user
        # Filtrar según rol
        if user.role == "ADMIN":
            return Usuario.objects.all()
        elif user.role == "APOYO":
            return (
                Usuario.objects.all()
            )  # Apoyo puede ver todo, no editar (depende del permiso)
        elif user.role == "DOCENTE":
            return Usuario.objects.filter(departamento=user.departamento)
        else:  # INVITADO
            return Usuario.objects.none()
