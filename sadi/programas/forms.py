from django import forms
from .models import ProgramaEstrategico, Ciclo


class ProgramaEstrategicoForm(forms.ModelForm):
    class Meta:
        model = ProgramaEstrategico
        fields = [
            "clave",
            "estado",
            "nombre",
            "nombre_corto",
            "fecha_inicio",
            "fecha_fin",
        ]
        widgets = {
            "clave": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "estado": forms.Select(attrs={"class": "form-control", "required": True}),
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "nombre_corto": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "fecha_inicio": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "required": True}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "required": True}
            ),
        }


class CicloForm(forms.ModelForm):
    class Meta:
        model = Ciclo
        fields = ["estado", "fecha_inicio", "fecha_fin", "programa"]
        widgets = {
            "estado": forms.Select(attrs={"class": "form-select", "required": True}),
            "fecha_inicio": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "required": True}
            ),
            "fecha_fin": forms.DateInput(
                attrs={"type": "date", "class": "form-control", "required": True}
            ),
            "programa": forms.Select(attrs={"class": "form-control", "required": True}),
        }
