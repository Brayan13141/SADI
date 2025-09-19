from rest_framework import serializers
from .models import Riesgo, Mitigacion


class MitigacionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mitigacion
        fields = ["id", "accion", "fecha_accion", "responsable", "riesgo"]


class RiesgoDetailSerializer(serializers.ModelSerializer):
    mitigaciones = MitigacionDetailSerializer(
        source="mitigacion_set", many=True, read_only=True
    )

    class Meta:
        model = Riesgo
        fields = [
            "id",
            "enunciado",
            "meta",
            "probabilidad",
            "impacto",
            "riesgo",
            "mitigaciones",
        ]
