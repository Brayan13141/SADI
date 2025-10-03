from django_filters.rest_framework import FilterSet, CharFilter
from .models import Departamento


class DepartamentoFilter(FilterSet):
    nombre = CharFilter(field_name="nombre", lookup_expr="icontains")

    class Meta:
        model = Departamento
        fields = ["nombre"]
