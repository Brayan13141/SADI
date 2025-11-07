from rest_framework import serializers
from .models import Meta, AvanceMeta, MetaComprometida, MetaCiclo
from proyectos.serializers import ProyectoSerializer
from departamentos.serializers import DepartamentoSerializer


# AvanceMeta simple
class AvanceMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvanceMeta
        fields = ["id", "avance", "fecha_registro", "departamento", "ciclo"]


# MetaComprometida simple
class MetaComprometidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaComprometida
        fields = ["id", "valor", "ciclo"]


# Nuevo: MetaCiclo simple
class MetaCicloSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaCiclo
        fields = ["id", "ciclo", "lineaBase", "metaCumplir"]


# Serializer de detalle de Meta con anidados
class MetaDetailSerializer(serializers.ModelSerializer):
    avances = AvanceMetaSerializer(source="avancemeta_set", many=True, read_only=True)
    comprometidas = MetaComprometidaSerializer(
        source="metacomprometida_set", many=True, read_only=True
    )
    metaciclos = MetaCicloSerializer(source="metaciclo_set", many=True, read_only=True)

    proyecto = ProyectoSerializer(read_only=True)
    departamento = DepartamentoSerializer(read_only=True)

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
            "variableB",
            # anidados
            "metaciclos",
            "avances",
            "comprometidas",
        ]
