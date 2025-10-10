from django.urls import path
from . import views

urlpatterns = [
    path("", views.gestion_reportes, name="reportes"),
    path("metas/", views.reporte_metas_departamento, name="reporte_metas_departamento"),
]
