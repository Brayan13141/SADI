from rest_framework import serializers
from .models import Actividad, Evidencia, SolicitudReapertura
from riesgos.models import Riesgo, Mitigacion


# --- Serializers de Riesgos y Mitigaciones anidados ---
class MitigacionNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mitigacion
        fields = ["id", "accion", "fecha_accion", "responsable"]


class RiesgoNestedSerializer(serializers.ModelSerializer):
    mitigaciones = MitigacionNestedSerializer(
        many=True, source="mitigacion_set", read_only=True
    )

    class Meta:
        model = Riesgo
        fields = [
            "id",
            "enunciado",
            "probabilidad",
            "impacto",
            "riesgo",
            "mitigaciones",
        ]


# --- Evidencias y Solicitudes ---
class EvidenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidencia
        fields = ["id", "archivo", "fecha_subida", "actividad"]
        read_only_fields = ["fecha_subida"]


class SolicitudReaperturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudReapertura
        fields = [
            "id",
            "actividad",
            "usuario",
            "departamento",
            "fecha_solicitud",
            "aprobada",
            "terminada",
        ]
        read_only_fields = ["fecha_solicitud", "usuario"]


# --- Actividad con riesgos y mitigaciones ---
class ActividadDetailSerializer(serializers.ModelSerializer):
    riesgos = RiesgoNestedSerializer(source="riesgo_set", many=True, read_only=True)
    evidencias = EvidenciaSerializer(many=True, read_only=True)

    class Meta:
        model = Actividad
        fields = [
            "id",
            "nombre",
            "descripcion",
            "estado",
            "fecha_inicio",
            "fecha_fin",
            "editable",
            "meta",
            "ciclo",
            "responsable",
            "departamento",
            "riesgos",
            "evidencias",
        ]
