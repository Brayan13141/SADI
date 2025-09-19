# actividades/serializers.py
from rest_framework import serializers
from .models import Actividad
from riesgos.serializers import RiesgoDetailSerializer


class ActividadDetailSerializer(serializers.ModelSerializer):
    riesgos = RiesgoDetailSerializer(source="riesgo_set", many=True, read_only=True)

    class Meta:
        model = Actividad
        fields = [
            "id",
            "descripcion",
            "meta",
            "responsable",
            "departamento",
            "estado",
            "fecha_inicio",
            "fecha_fin",
            "riesgos",
        ]
