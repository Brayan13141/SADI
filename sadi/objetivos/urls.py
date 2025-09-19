from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ObjetivoEstrategicoViewSet, gestion_objetivos, objetivo_json

router = DefaultRouter()
router.register(r"api/objetivos", ObjetivoEstrategicoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", gestion_objetivos, name="gestion_objetivos"),
    path("admin/<int:objetivo_id>/json/", objetivo_json, name="objetivo_json"),
]
