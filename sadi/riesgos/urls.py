from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RiesgoViewSet,
    MitigacionViewSet,
    gestion_riesgos,
    gestion_mitigaciones,
)

router = DefaultRouter()
router.register(r"api/riesgos", RiesgoViewSet, basename="riesgos")
router.register(r"api/mitigaciones", MitigacionViewSet, basename="mitigaciones")

urlpatterns = [
    path("", include(router.urls)),
    path("admin/riesgos/", gestion_riesgos, name="gestion_riesgos"),
    path("admin/mitigaciones/", gestion_mitigaciones, name="gestion_mitigaciones"),
]
