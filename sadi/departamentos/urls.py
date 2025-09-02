from django import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartamentoViewSet, gestion_departamentos

router = DefaultRouter()
router.register(r"api/departamentos", DepartamentoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", gestion_departamentos, name="gestion_departamentos"),
]
