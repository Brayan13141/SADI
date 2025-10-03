from django_filters.rest_framework import FilterSet, DateFromToRangeFilter, CharFilter
from .models import Actividad


class ActividadFilter(FilterSet):
    # Rangos de fechas
    fecha_inicio = DateFromToRangeFilter()
    fecha_fin = DateFromToRangeFilter()

    # Búsqueda parcial en descripción
    descripcion = CharFilter(field_name="descripcion", lookup_expr="icontains")

    class Meta:
        model = Actividad
        # Campos que se pueden filtrar desde la URL
        fields = ["meta", "departamento", "responsable", "estado", "descripcion"]
