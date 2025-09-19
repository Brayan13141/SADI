from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ObjetivoEstrategicoViewSet, gestion_objetivos

router = DefaultRouter()
router.register(r"api/objetivos", ObjetivoEstrategicoViewSet, basename="objetivos")

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", gestion_objetivos, name="gestion_objetivos"),
]
