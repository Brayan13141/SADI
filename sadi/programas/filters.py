from django_filters.rest_framework import (
    FilterSet,
    CharFilter,
    BooleanFilter,
    DateFromToRangeFilter,
)
from .models import ProgramaEstrategico, Ciclo


class ProgramaEstrategicoFilter(FilterSet):
    nombre = CharFilter(field_name="nombre", lookup_expr="icontains")
    nombre_corto = CharFilter(field_name="nombre_corto", lookup_expr="icontains")
    clave = CharFilter(field_name="clave", lookup_expr="icontains")
    estado = BooleanFilter(field_name="estado")
    fecha_inicio = DateFromToRangeFilter()
    fecha_fin = DateFromToRangeFilter()

    class Meta:
        model = ProgramaEstrategico
        fields = ["estado", "clave"]


class CicloFilter(FilterSet):
    activo = BooleanFilter(field_name="activo")
    fecha_inicio = DateFromToRangeFilter()
    fecha_fin = DateFromToRangeFilter()

    class Meta:
        model = Ciclo
        fields = ["activo", "programa"]
