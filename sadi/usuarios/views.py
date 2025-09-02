from .models import Usuario
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UsuarioEditForm, UsuarioForm
from django.http import JsonResponse


@login_required
def crud_usuarios(request):
    usuarios = Usuario.objects.all()
    form = UsuarioForm()
    abrir_modal_crear = False

    if request.method == "POST":
        if "crear_usuario" in request.POST:
            form = UsuarioForm(request.POST)
            if form.is_valid():
                usuario = form.save(commit=False)

                messages.success(request, "Usuario creado correctamente.")
                return redirect("gestion_usuarios")

            else:
                # Marcar para abrir el modal de creación con errores
                abrir_modal_crear = True

        elif "editar_usuario" in request.POST:
            usuario_id = request.POST.get("usuario_id")
            usuario = get_object_or_404(Usuario, id=usuario_id)
            form = UsuarioEditForm(request.POST, instance=usuario)
            if form.is_valid():
                form.save()
                messages.success(request, "Usuario editado correctamente.")
                return redirect("gestion_usuarios")
            else:
                # Si hay errores en la edición, devolverlos como JSON para mostrarlos en el modal
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    # Convertir errores a formato serializable
                    errors = {}
                    for field, error_list in form.errors.items():
                        errors[field] = [str(error) for error in error_list]
                    return JsonResponse({"errors": errors}, status=400)

                # Si no es AJAX, recargar la página
                messages.error(request, "Error al editar el usuario.")

        elif "eliminar_usuario" in request.POST:
            usuario_id = request.POST.get("usuario_id")
            usuario = get_object_or_404(Usuario, id=usuario_id)
            usuario.delete()
            messages.success(request, "Usuario eliminado correctamente.")
            return redirect("gestion_usuarios")

    return render(
        request,
        "usuarios/crud_usuarios.html",
        {"usuarios": usuarios, "form": form, "abrir_modal_crear": abrir_modal_crear},
    )
