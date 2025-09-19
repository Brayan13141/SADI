from django import forms
from .models import Riesgo, Mitigacion
from metas.models import Meta
from usuarios.models import Usuario


class RiesgoForm(forms.ModelForm):
    class Meta:
        model = Riesgo
        fields = ["enunciado", "probabilidad", "impacto", "meta"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["meta"].queryset = Meta.objects.all()


class MitigacionForm(forms.ModelForm):
    class Meta:
        model = Mitigacion
        fields = ["accion", "fecha_accion", "responsable", "riesgo"]
        widgets = {
            "fecha_accion": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["responsable"].queryset = Usuario.objects.all()
        self.fields["riesgo"].queryset = Riesgo.objects.all()
