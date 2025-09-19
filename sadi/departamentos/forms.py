from django import forms
from .models import Departamento


class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ["nombre"]

    widgets = {
        "nombre": forms.TextInput(attrs={"class": "form-control", "required": True})
    }
