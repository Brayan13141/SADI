from django import forms
from django.utils import timezone
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
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            if user.role == "DOCENTE":
                # Filtrar metas solo por departamento del docente
                self.fields["meta"].queryset = Meta.objects.filter(
                    activa=True, departamento=user.departamento
                ).order_by("id")
            else:
                self.fields["meta"].queryset = (
                    Meta.objects.all().filter(activa=True).order_by("id")
                )


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
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        hoy = timezone.now().date().strftime("%Y-%m-%d")
        self.fields["fecha_accion"].widget.attrs.update(
            {
                "min": hoy,
                "value": hoy,
            }
        )
        self.fields["responsable"].queryset = Usuario.objects.all()
        if user:
            if user.role == "DOCENTE":
                # Filtrar riesgos solo por departamento del docente
                self.fields["riesgo"].queryset = Riesgo.objects.filter(
                    meta__departamento=user.departamento
                )
            else:
                self.fields["riesgo"].queryset = Riesgo.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        fecha_accion = cleaned_data.get("fecha_accion")

        if fecha_accion:
            if fecha_accion < timezone.now().date():
                self.add_error(
                    "fecha_accion", "La fecha de acción no puede ser anterior a hoy"
                )

        return cleaned_data
