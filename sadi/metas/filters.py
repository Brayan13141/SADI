from django_filters.rest_framework import FilterSet, CharFilter, BooleanFilter
from .models import Meta


class MetaFilter(FilterSet):
    nombre = CharFilter(field_name="nombre", lookup_expr="icontains")
    clave = CharFilter(field_name="clave", lookup_expr="icontains")
    enunciado = CharFilter(field_name="enunciado", lookup_expr="icontains")
    indicador = CharFilter(field_name="indicador", lookup_expr="icontains")
    activa = BooleanFilter(field_name="activa")

    class Meta:
        model = Meta
        fields = ["proyecto", "departamento", "activa", "ciclo"]
