from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProyectoViewSet, gestion_proyectos

router = DefaultRouter()
router.register(r"api/proyectos", ProyectoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", gestion_proyectos, name="gestion_proyectos"),
]
