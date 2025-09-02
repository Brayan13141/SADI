from rest_framework import serializers
from .models import Proyecto
from objetivos.serializers import ObjetivoEstrategicoSerializer


class ProyectoSerializer(serializers.ModelSerializer):
    objetivo_detail = ObjetivoEstrategicoSerializer(source="objetivo", read_only=True)

    class Meta:
        model = Proyecto
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}}
