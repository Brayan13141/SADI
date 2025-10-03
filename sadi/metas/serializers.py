from rest_framework import serializers
from .models import Meta, AvanceMeta, MetaComprometida
from proyectos.serializers import ProyectoSerializer
from departamentos.serializers import DepartamentoSerializer


# AvanceMeta simple
class AvanceMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvanceMeta
        fields = ["id", "avance", "fecha_registro", "departamento"]


# MetaComprometida simple
class MetaComprometidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaComprometida
        fields = ["id", "valor"]


# Serializer de detalle de Meta con anidado
class MetaDetailSerializer(serializers.ModelSerializer):
    avances = AvanceMetaSerializer(source="avancemeta_set", many=True, read_only=True)
    comprometidas = MetaComprometidaSerializer(
        source="metacomprometida_set", many=True, read_only=True
    )

    class Meta:
        model = Meta
        fields = [
            "id",
            "nombre",
            "clave",
            "enunciado",
            "proyecto",
            "departamento",
            "indicador",
            "unidadMedida",
            "porcentages",
            "activa",
            "metodoCalculo",
            "lineabase",
            "metacumplir",
            "variableB",
            "ciclo",
            "avances",
            "comprometidas",
        ]
