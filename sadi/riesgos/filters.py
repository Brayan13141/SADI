from django_filters.rest_framework import (
    FilterSet,
    CharFilter,
    NumberFilter,
    DateFromToRangeFilter,
)
from .models import Riesgo, Mitigacion


class RiesgoFilter(FilterSet):
    enunciado = CharFilter(field_name="enunciado", lookup_expr="icontains")
    probabilidad_min = NumberFilter(field_name="probabilidad", lookup_expr="gte")
    probabilidad_max = NumberFilter(field_name="probabilidad", lookup_expr="lte")
    impacto_min = NumberFilter(field_name="impacto", lookup_expr="gte")
    impacto_max = NumberFilter(field_name="impacto", lookup_expr="lte")
    riesgo_min = NumberFilter(field_name="riesgo", lookup_expr="gte")
    riesgo_max = NumberFilter(field_name="riesgo", lookup_expr="lte")

    class Meta:
        model = Riesgo
        fields = ["meta", "probabilidad", "impacto", "riesgo"]


class MitigacionFilter(FilterSet):
    accion = CharFilter(field_name="accion", lookup_expr="icontains")
    fecha_accion = DateFromToRangeFilter()
    responsable = CharFilter(
        field_name="responsable__username", lookup_expr="icontains"
    )

    class Meta:
        model = Mitigacion
        fields = ["riesgo", "responsable", "fecha_accion"]
