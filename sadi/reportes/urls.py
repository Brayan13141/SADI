from django.urls import path
from . import views

urlpatterns = [
    path("", views.gestion_reportes, name="reportes"),
    path("metas/", views.reporte_metas_departamento, name="reporte_metas_departamento"),
    path("programas/", views.reporte_proyectos, name="reporte_programas"),
    path("avances/", views.reporte_avances_metas, name="reporte_avances_metas"),
    path("riesgos/", views.reporte_riesgos, name="reporte_riesgos"),
    path("docentes/", views.reporte_general_docente, name="reporte_docente"),
]
