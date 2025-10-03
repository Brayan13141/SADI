from django_filters.rest_framework import FilterSet, CharFilter
from .models import ObjetivoEstrategico


class ObjetivoEstrategicoFilter(FilterSet):
    descripcion = CharFilter(field_name="descripcion", lookup_expr="icontains")

    class Meta:
        model = ObjetivoEstrategico
        fields = ["ciclo", "programa"]
