from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

from .views import (
    MetaViewSet,
    AvanceMetaViewSet,
    MetaComprometidaViewSet,
    TablaSeguimiento,
    gestion_metas,
    gestion_avances_meta,
    gestion_metas_comprometidas,
)

router = DefaultRouter()
router.register(r"api/metas", MetaViewSet)
router.register(r"api/avances-meta", AvanceMetaViewSet)
router.register(r"api/metas-comprometidas", MetaComprometidaViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("tablaSeguimiento/", TablaSeguimiento, name="tabla_seguimiento"),
    path("admin/", gestion_metas, name="gestion_metas"),
    path("admin/<int:meta_id>/json/", views.meta_json, name="meta_json"),
    path(
        "admin/<int:meta_id>/avances/",
        gestion_avances_meta,
        name="gestion_avances_meta",
    ),
    path(
        "admin/<int:meta_id>/comprometidas/",
        gestion_metas_comprometidas,
        name="gestion_metas_comprometidas",
    ),
]
