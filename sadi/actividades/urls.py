from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ActividadViewSet,
    gestion_actividades,
    ver_actividades,
    agregar_actividad,
)

router = DefaultRouter()
router.register(r"api/actividades", ActividadViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", gestion_actividades, name="gestion_actividades"),
    path("meta/<int:meta_id>/actividades/", ver_actividades, name="ver_actividades"),
    path(
        "meta/<int:meta_id>/agregar-actividad/",
        agregar_actividad,
        name="agregar_actividad",
    ),
]
