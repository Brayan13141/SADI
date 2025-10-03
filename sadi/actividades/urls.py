from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActividadViewSet,
    EvidenciaViewSet,
    SolicitudReaperturaViewSet,
    gestion_actividades,
    ver_actividades,
    agregar_actividad,
    ProgramaTrabajo,
    programa_trabajo_pdf,
    solicitudes_reapertura,
)

router = DefaultRouter()
router.register(r"api/actividades", ActividadViewSet, basename="actividad")
router.register(r"api/evidencias", EvidenciaViewSet, basename="evidencia")
router.register(
    r"api/solicitudes-reapertura",
    SolicitudReaperturaViewSet,
    basename="solicitud_reapertura",
)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", gestion_actividades, name="gestion_actividades"),
    path("programa-trabajo/", ProgramaTrabajo, name="programa_trabajo"),
    path("programa-trabajo/pdf/", programa_trabajo_pdf, name="programa_trabajo_pdf"),
    path(
        "solicitudes/reapertura/",
        solicitudes_reapertura,
        name="solicitudes_reapertura",
    ),
    path("meta/<int:meta_id>/actividades/", ver_actividades, name="ver_actividades"),
    path(
        "meta/<int:meta_id>/agregar-actividad/",
        agregar_actividad,
        name="agregar_actividad",
    ),
]
