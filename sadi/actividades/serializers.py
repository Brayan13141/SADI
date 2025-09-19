from rest_framework import serializers
from .models import Actividad


class ActividadSerializer(serializers.ModelSerializer):
    # meta_detail = MetaSerializer(source="meta", read_only=True)
    # responsable_detail = UsuarioSerializer(source="responsable", read_only=True)

    class Meta:
        model = Actividad
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}}
