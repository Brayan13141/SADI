from rest_framework import serializers
from .models import Meta, AvanceMeta, MetaComprometida
from proyectos.serializers import ProyectoSerializer
from departamentos.serializers import DepartamentoSerializer


class MetaSerializer(serializers.ModelSerializer):
    # proyecto_detail = ProyectoSerializer(source="proyecto", read_only=True)
    # departamento_detail = DepartamentoSerializer(source="departamento", read_only=True)

    class Meta:
        model = Meta
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}}


class AvanceMetaSerializer(serializers.ModelSerializer):
    # meta_detail = MetaSerializer(source="metaCumplir", read_only=True)
    # departamento_detail = DepartamentoSerializer(source="departamento", read_only=True)

    class Meta:
        model = AvanceMeta
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}}


class MetaComprometidaSerializer(serializers.ModelSerializer):
    # meta_detail = MetaSerializer(source="meta", read_only=True)
    # departamento_detail = DepartamentoSerializer(source="departamento", read_only=True)

    class Meta:
        model = MetaComprometida
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}}
