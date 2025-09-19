from rest_framework import serializers
from .models import Departamento


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}}
