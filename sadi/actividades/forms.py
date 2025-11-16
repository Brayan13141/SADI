from django.utils import timezone
from django import forms
from .models import Actividad, Evidencia, SolicitudReapertura
from metas.models import Meta
from usuarios.models import Usuario


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = [
            "estado",
            "nombre",
            "descripcion",
            "fecha_inicio",
            "fecha_fin",
            "departamento",
            "meta",
            "responsable",
            "editable",
        ]
        widgets = {
            "estado": forms.Select(attrs={"class": "form-select", "required": True}),
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "required": True, "id": "id_nombre"}
            ),
            "descripcion": forms.Textarea(
                attrs={"rows": 3, "class": "form-control", "required": True}
            ),
            "fecha_inicio": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "required": True,
                    "id": "id_fecha_inicio",
                }
            ),
            "fecha_fin": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "required": True,
                    "id": "id_fecha_fin",
                }
            ),
            "meta": forms.Select(attrs={"class": "form-select", "required": True}),
            "responsable": forms.Select(
                attrs={"class": "form-select", "required": True}
            ),
            "editable": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            if user.role == "DOCENTE":
                # Filtrar metas solo por departamento del docente
                self.fields["meta"].queryset = Meta.objects.filter(
                    departamento=user.departamento
                )
            else:
                # Admin y Apoyo ven todas las metas
                self.fields["meta"].queryset = Meta.objects.all()

            # Responsables disponibles
            if user.role == "DOCENTE":
                # Solo el docente puede seleccionarse a sí mismo
                self.fields["responsable"].queryset = Usuario.objects.filter(id=user.id)
            else:
                # Admin y Apoyo ven todos
                self.fields["responsable"].queryset = Usuario.objects.all()

    def clean(self):
        cleaned_data = super().clean()

        return cleaned_data


class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = Evidencia
        fields = ["archivo"]


class SolicitudReaperturaForm(forms.ModelForm):
    class Meta:
        model = SolicitudReapertura
        fields = []  # no mostramos nada, solo se llena automático en la view
