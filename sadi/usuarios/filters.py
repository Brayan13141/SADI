from django_filters.rest_framework import (
    FilterSet,
    CharFilter,
    NumberFilter,
    DateFromToRangeFilter,
)
from .models import Usuario


class UsuarioFilter(FilterSet):
    username = CharFilter(field_name="username", lookup_expr="icontains")
    first_name = CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = CharFilter(field_name="last_name", lookup_expr="icontains")
    email = CharFilter(field_name="email", lookup_expr="icontains")

    class Meta:
        model = Usuario
        fields = ["role", "departamento"]
