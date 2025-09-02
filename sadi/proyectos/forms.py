from django import forms
from .models import Proyecto
from objetivos.models import ObjetivoEstrategico


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ["clave", "nombre", "objetivo"]
        widgets = {
            "nombre": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["objetivo"].queryset = ObjetivoEstrategico.objects.all()
