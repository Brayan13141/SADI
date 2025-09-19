from django import forms
from .models import Actividad
from metas.models import Meta
from usuarios.models import Usuario


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = [
            "estado",
            "descripcion",
            "fecha_inicio",
            "fecha_fin",
            "evidencia",
            "meta",
            "responsable",
        ]
        widgets = {
            "estado": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "descripcion": forms.Textarea(
                attrs={"rows": 3, "class": "form-control", "required": True}
            ),
            "fecha_inicio": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "required": True}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "required": True}
            ),
            "evidencia": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "meta": forms.Select(attrs={"class": "form-control", "required": True}),
            "responsable": forms.Select(
                attrs={"class": "form-control", "required": True}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mejorar la visualización de los campos ForeignKey
        self.fields["meta"].queryset = Meta.objects.all()
        self.fields["responsable"].queryset = Usuario.objects.all()
