# actividades/serializers.py
from rest_framework import serializers
from .models import Actividad, Evidencia, SolicitudReapertura
from riesgos.serializers import RiesgoDetailSerializer


class ActividadDetailSerializer(serializers.ModelSerializer):
    riesgos = RiesgoDetailSerializer(source="riesgo_set", many=True, read_only=True)

    class Meta:
        model = Actividad
        fields = [
            "id",
            "nombre",
            "descripcion",
            "meta",
            "responsable",
            "departamento",
            "estado",
            "fecha_inicio",
            "fecha_fin",
            "riesgos",
        ]


class EvidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidencia
        fields = "__all__"  # Includes: 'id', 'actividad', 'archivo', 'fecha_subida'
        read_only_fields = ("fecha_subida",)  # This field is set automatically


class SolicitudReaperturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudReapertura
        fields = "__all__"  # Includes: 'id', 'actividad', 'usuario', 'departamento', 'fecha_solicitud', 'aprobada'
        read_only_fields = (
            "fecha_solicitud",
            "usuario",
        )  # Usuario will be set in the view
