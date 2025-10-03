from rest_framework import serializers
from .models import ProgramaEstrategico, Ciclo


class CicloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciclo
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}}


class ProgramaEstrategicoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProgramaEstrategico
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}}
