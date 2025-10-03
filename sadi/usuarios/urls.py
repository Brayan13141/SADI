from django.urls import include, path
from .views import UsuarioViewSet, gestion_usuarios
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"api/usuarios", UsuarioViewSet, basename="usuarios")


urlpatterns = [
    path("", include(router.urls)),
    path("admin/", gestion_usuarios, name="gestion_usuarios"),
]
