from django import forms
from .models import Riesgo, Mitigacion
from metas.models import Meta
from usuarios.models import Usuario


class RiesgoForm(forms.ModelForm):
    class Meta:
        model = Riesgo
        fields = ["enunciado", "probabilidad", "impacto", "meta"]
        widgets = {
            "enunciado": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "probabilidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "min": 1,
                    "max": 10,
                    "onchange": "calcularRiesgo()",
                }
            ),
            "impacto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "min": 1,
                    "max": 10,
                    "onchange": "calcularRiesgo()",
                }
            ),
            "meta": forms.Select(attrs={"class": "form-select", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["meta"].queryset = Meta.objects.all()


class MitigacionForm(forms.ModelForm):
    class Meta:
        model = Mitigacion
        fields = ["accion", "fecha_accion", "responsable", "riesgo"]
        widgets = {
            "accion": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "fecha_accion": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "required": True}
            ),
            "responsable": forms.Select(
                attrs={"class": "form-select", "required": True}
            ),
            "riesgo": forms.Select(attrs={"class": "form-select", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsable"].queryset = Usuario.objects.all()
        self.fields["riesgo"].queryset = Riesgo.objects.all()
