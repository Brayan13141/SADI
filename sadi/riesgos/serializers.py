from rest_framework import serializers
from .models import Riesgo, Mitigacion


class MitigacionSerializer(serializers.ModelSerializer):
    # responsable_detail = UsuarioSerializer(source="responsable", read_only=True)
    # riesgo_detail = serializers.SerializerMethodField()

    class Meta:
        model = Mitigacion
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}}

    def get_riesgo_detail(self, obj):
        from .serializers import RiesgoSerializer

        return RiesgoSerializer(obj.riesgo).data


class RiesgoSerializer(serializers.ModelSerializer):
    # meta_detail = MetaSerializer(source="meta", read_only=True)
    # mitigaciones = MitigacionSerializer(many=True, read_only=True)

    class Meta:
        model = Riesgo
        fields = "__all__"
        extra_kwargs = {"history": {"read_only": True}, "riesgo": {"read_only": True}}
