from django_filters.rest_framework import FilterSet, CharFilter
from .models import Proyecto


class ProyectoFilter(FilterSet):
    clave = CharFilter(field_name="clave", lookup_expr="icontains")
    nombre = CharFilter(field_name="nombre", lookup_expr="icontains")

    class Meta:
        model = Proyecto
        fields = ["objetivo"]
