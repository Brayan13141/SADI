from django import forms
from .models import ObjetivoEstrategico
from programas.models import ProgramaEstrategico, Ciclo


class ObjetivoEstrategicoForm(forms.ModelForm):
    class Meta:
        model = ObjetivoEstrategico
        fields = ["descripcion", "ciclo", "programa"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar ciclos y programas relacionados
        self.fields["ciclo"].queryset = Ciclo.objects.all()
        self.fields["programa"].queryset = ProgramaEstrategico.objects.all()
