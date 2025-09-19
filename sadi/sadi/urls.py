from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("core.urls")),
    path("auth/", include("dj_rest_auth.urls")),  # login/logout/user(API)
    path("departamentos/", include("departamentos.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("programas/", include("programas.urls")),
    path("objetivos/", include("objetivos.urls")),
    path("proyectos/", include("proyectos.urls")),
    path("metas/", include("metas.urls")),
    path("actividades/", include("actividades.urls")),
    path("riesgos/", include("riesgos.urls")),
]
