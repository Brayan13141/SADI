from django import forms
from .models import Meta, AvanceMeta, MetaComprometida
from proyectos.models import Proyecto
from departamentos.models import Departamento
from programas.models import ProgramaEstrategico


class MetaForm(forms.ModelForm):
    class Meta:
        model = Meta
        fields = [
            "nombre",
            "clave",
            "enunciado",
            "proyecto",
            "departamento",
            "indicador",
            "unidadMedida",
            "porcentages",
            "activa",
            "metodoCalculo",
            "lineabase",
            "metacumplir",
            "variableB",
        ]
        widgets = {
            "enunciado": forms.Textarea(attrs={"rows": 3}),
            "indicador": forms.Textarea(attrs={"rows": 3}),
            "metodoCalculo": forms.Textarea(attrs={"rows": 3}),
            "lineabase": forms.NumberInput(attrs={"step": "0.0001"}),
            "metacumplir": forms.NumberInput(attrs={"step": "0.0001"}),
            "variableB": forms.NumberInput(attrs={"step": "0.0001"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["proyecto"].queryset = Proyecto.objects.all()
        self.fields["departamento"].queryset = Departamento.objects.all()


class AvanceMetaForm(forms.ModelForm):
    class Meta:
        model = AvanceMeta
        fields = ["avance", "fecha_registro", "metaCumplir", "departamento"]
        widgets = {
            "fecha_registro": forms.DateInput(attrs={"type": "date"}),
            "avance": forms.NumberInput(attrs={"step": "0.0001"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["metaCumplir"].queryset = Meta.objects.all()
        self.fields["departamento"].queryset = Departamento.objects.all()


class MetaComprometidaForm(forms.ModelForm):
    class Meta:
        model = MetaComprometida
        fields = ["valor", "meta", "programa"]
        widgets = {
            "valor": forms.NumberInput(attrs={"step": "0.0001"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["meta"].queryset = Meta.objects.all()
        self.fields["programa"].queryset = ProgramaEstrategico.objects.all()
