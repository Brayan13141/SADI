from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProgramaEstrategicoViewSet,
    CicloViewSet,
    gestion_programas,
    gestion_ciclos,
)

router = DefaultRouter()
# programas/urls.py
router.register(r"api/programas", ProgramaEstrategicoViewSet, basename="programas")
router.register(r"api/ciclos", CicloViewSet, basename="ciclos")


urlpatterns = [
    path("", include(router.urls)),
    path("admin/", gestion_programas, name="gestion_programas"),
    path("adminc/", gestion_ciclos, name="gestion_ciclos"),
]
