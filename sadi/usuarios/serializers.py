from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    departamento_nombre = serializers.CharField(
        source="departamento.nombre", read_only=True
    )

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "departamento",
            "departamento_nombre",
        ]
        read_only_fields = ["is_staff", "is_superuser"]  # Solo admin puede modificarlos
