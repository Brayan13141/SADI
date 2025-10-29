from django import forms
from .models import ObjetivoEstrategico
from programas.models import ProgramaEstrategico, Ciclo


class ObjetivoEstrategicoForm(forms.ModelForm):
    class Meta:
        model = ObjetivoEstrategico
        fields = ["descripcion", "programa"]
        widgets = {
            "descripcion": forms.Textarea(
                attrs={"rows": 3, "class": "form-control", "required": True}
            ),
            # "ciclo": forms.Select(attrs={"class": "form-select", "required": True}),
            "programa": forms.Select(attrs={"class": "form-select", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["programa"].queryset = ProgramaEstrategico.objects.all()
