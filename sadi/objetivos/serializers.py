from rest_framework import serializers
from .models import ObjetivoEstrategico
from programas.serializers import CicloSerializer, ProgramaEstrategicoSerializer


class ObjetivoEstrategicoSerializer(serializers.ModelSerializer):
    #ciclo_detail = CicloSerializer(source="ciclo", read_only=True)
    #programa_detail = ProgramaEstrategicoSerializer(source="programa", read_only=True)

    class Meta:
        model = ObjetivoEstrategico
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}}
