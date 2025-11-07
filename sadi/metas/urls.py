from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MetaViewSet,
    AvanceMetaViewSet,
    MetaComprometidaViewSet,
    TablaSeguimiento,
    gestion_metas,
    gestion_meta_avances,
    gestion_meta_comprometida,
    avance_meta_general_list,
    meta_comprometida_general_list,
    asignacion_metas,
    activar_metas,
    asignar_ciclo_meta,
)

router = DefaultRouter()
router.register(r"api/metas", MetaViewSet, basename="metas")
router.register(r"api/avances-meta", AvanceMetaViewSet, basename="avances-meta")
router.register(
    r"api/metas-comprometidas", MetaComprometidaViewSet, basename="metas-comprometidas"
)

urlpatterns = [
    path("", include(router.urls)),
    path("tablaSeguimiento/", TablaSeguimiento, name="tabla_seguimiento"),
    path("admin/asignacion/", asignacion_metas, name="asignacion_metas"),
    path(
        "asignar_ciclo_meta/<int:meta_id>/",
        asignar_ciclo_meta,
        name="asignar_ciclo_meta",
    ),
    path("admin/", gestion_metas, name="gestion_metas"),
    path("admin/avances/", avance_meta_general_list, name="avance_meta_general_list"),
    path(
        "admin/comprometidas/",
        meta_comprometida_general_list,
        name="meta_comprometida_general_list",
    ),
    path("<int:meta_id>/detalle/", gestion_meta_avances, name="gestion_meta_avances"),
    path(
        "<int:meta_id>/comprometida/",
        gestion_meta_comprometida,
        name="gestion_meta_comprometida",
    ),
    path("admin/activar/", activar_metas, name="activar_metas"),
]
