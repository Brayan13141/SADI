from rest_framework import serializers
from .models import Riesgo, Mitigacion


class MitigacionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mitigacion
        fields = ["id", "accion", "fecha_accion", "responsable", "riesgo"]


class RiesgoDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Riesgo
        fields = [
            "id",
            "enunciado",
            "meta",
            "probabilidad",
            "impacto",
            "riesgo",
        ]
