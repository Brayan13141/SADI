from django import forms
from .models import Proyecto
from objetivos.models import ObjetivoEstrategico


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ["nombre", "objetivo"]
        widgets = {
            "nombre": forms.Textarea(
                attrs={"rows": 3, "class": "form-control", "required": True}
            ),
            "objetivo": forms.Select(attrs={"class": "form-select", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["objetivo"].queryset = ObjetivoEstrategico.objects.all()
