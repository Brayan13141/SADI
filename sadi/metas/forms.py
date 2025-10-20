from django.utils import timezone
from django import forms

from programas.models import Ciclo
from .models import Meta, AvanceMeta, MetaComprometida
from proyectos.models import Proyecto
from departamentos.models import Departamento


class MetaFormAdmin(forms.ModelForm):
    class Meta:
        model = Meta
        fields = [
            "nombre",
            "clave",
            "enunciado",
            "proyecto",
            "departamento",
            "indicador",
            "acumulable",
            "unidadMedida",
            "porcentages",
            "activa",
            "metodoCalculo",
            "lineabase",
            "metacumplir",
            "variableB",
            "ciclo",
        ]
        widgets = {
            "clave": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "enunciado": forms.Textarea(
                attrs={"rows": 3, "class": "form-control", "required": True}
            ),
            "proyecto": forms.Select(attrs={"class": "form-select", "required": True}),
            "acumulable": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "departamento": forms.Select(attrs={"class": "form-select"}),
            "indicador": forms.Textarea(
                attrs={"rows": 3, "class": "form-control", "required": True}
            ),
            "unidadMedida": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "porcentages": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "metodoCalculo": forms.Textarea(
                attrs={"rows": 3, "class": "form-control", "required": True}
            ),
            "lineabase": forms.NumberInput(attrs={"class": "form-control"}),
            "metacumplir": forms.NumberInput(attrs={"class": "form-control"}),
            "variableB": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "ciclo": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["proyecto"].queryset = Proyecto.objects.all()
        self.fields["departamento"].queryset = Departamento.objects.all()


class MetaFormDocente(forms.ModelForm):
    class Meta:
        model = Meta
        fields = [
            "nombre",
            "clave",
            "enunciado",
            "proyecto",
            "departamento",
            "indicador",
            "acumulable",
            "unidadMedida",
            "porcentages",
            "activa",
            "metodoCalculo",
            "lineabase",
            "metacumplir",
            "variableB",
            "ciclo",
        ]
        widgets = {
            "clave": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "enunciado": forms.Textarea(
                attrs={"rows": 3, "class": "form-control", "required": True}
            ),
            "proyecto": forms.Select(attrs={"class": "form-select", "disabled": True}),
            "acumulable": forms.CheckboxInput(
                attrs={"class": "form-check-input", "disabled": True}
            ),
            "departamento": forms.Select(
                attrs={"class": "form-select", "disabled": True}
            ),
            "indicador": forms.Textarea(
                attrs={"rows": 3, "class": "form-control", "required": True}
            ),
            "unidadMedida": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "porcentages": forms.CheckboxInput(
                attrs={"class": "form-check-input", "disabled": True}
            ),
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "metodoCalculo": forms.Textarea(
                attrs={"rows": 3, "class": "form-control", "required": True}
            ),
            "lineabase": forms.NumberInput(attrs={"class": "form-control"}),
            "metacumplir": forms.NumberInput(attrs={"class": "form-control"}),
            "variableB": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "ciclo": forms.Select(attrs={"class": "form-select", "disabled": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in [
            "clave",
            "nombre",
            "lineaBase",
            "enunciado",
            "indicador",
            "unidadMedida",
            "metodoCalculo",
            "proyecto",
            "activa",
            "departamento",
            "ciclo",
            "acumulable",
            "porcentages",
            "variableB",
        ]:
            if field_name in self.initial:
                self.fields[field_name].disabled = True


# ========================FORMULARIOS DE AVANCE Y COMPROMETIDA UNICA========================#
class AvanceMetaForm(forms.ModelForm):
    class Meta:
        model = AvanceMeta
        fields = ["avance", "fecha_registro", "metaCumplir", "departamento"]
        widgets = {
            "fecha_registro": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "required": True,
                    "id": "id_fecha_registro",
                }
            ),
            "avance": forms.NumberInput(
                attrs={"class": "form-control", "required": True, "id": "id_avance"}
            ),
            "metaCumplir": forms.HiddenInput(),
            "departamento": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        # Obtener la meta desde los argumentos si está disponible
        meta = kwargs.pop("meta", None)
        super().__init__(*args, **kwargs)

        # Establecer valores iniciales para campos hidden
        if meta:
            self.fields["metaCumplir"].initial = meta.id
            self.fields["departamento"].initial = (
                meta.departamento.id if meta.departamento else None
            )
        hoy = timezone.now().date().strftime("%Y-%m-%d")
        self.fields["fecha_registro"].widget.attrs.update(
            {
                "min": hoy,
                "value": hoy,
            }
        )

    def clean_avance(self):
        avance = self.cleaned_data.get("avance")
        if avance is not None:
            if avance < 0:
                raise forms.ValidationError("El avance no puede ser negativo.")
            if avance > 100:
                raise forms.ValidationError("El avance no puede ser mayor a 100%.")
        return avance


class MetaComprometidaForm(forms.ModelForm):
    class Meta:
        model = MetaComprometida
        fields = ["valor", "meta"]
        widgets = {
            "valor": forms.NumberInput(
                attrs={"class": "form-control", "required": True}
            ),
            "meta": forms.HiddenInput(),
        }

    def clean_valor(self):
        valor = self.cleaned_data.get("valor")
        if valor is not None and valor < 0:
            raise forms.ValidationError("El valor no puede ser negativo.")
        return valor


# ========================FORMULARIOS DE AVANCE Y COMPROMETIDA MASIVO========================#
class AvanceMetaGeneralForm(forms.ModelForm):
    class Meta:
        model = AvanceMeta
        fields = ["avance", "fecha_registro", "metaCumplir", "departamento"]
        widgets = {
            "fecha_registro": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                    "required": True,
                }
            ),
            "avance": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "min": 0,
                    "max": 100,
                    "step": 0.01,
                }
            ),
            "metaCumplir": forms.Select(
                attrs={"class": "form-select", "required": True, "id": "id_metaCumplir"}
            ),
            "departamento": forms.Select(
                attrs={"class": "form-select", "id": "id_departamento"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["metaCumplir"].queryset = Meta.objects.all()
        self.fields["departamento"].queryset = Departamento.objects.all()
        self.fields["departamento"].required = False  # Hacer que no sea obligatorio

        hoy = timezone.now().date().strftime("%Y-%m-%d")
        self.fields["fecha_registro"].widget.attrs.update(
            {
                "min": hoy,
                "value": hoy,
            }
        )

    def clean_avance(self):
        avance = self.cleaned_data.get("avance")
        if avance is not None:
            if avance < 0:
                raise forms.ValidationError("El avance no puede ser negativo.")
            if avance > 100:
                raise forms.ValidationError("El avance no puede ser mayor a 100%.")
        else:
            raise forms.ValidationError("El avance es obligatorio.")
        return avance


class MetaComprometidaGeneralForm(forms.ModelForm):
    class Meta:
        model = MetaComprometida
        fields = ["valor", "meta"]
        widgets = {
            "valor": forms.NumberInput(
                attrs={"class": "form-control", "required": True}
            ),
            "meta": forms.Select(attrs={"class": "form-select", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["meta"].queryset = Meta.objects.all().order_by("id")
        # Hacer todos los campos obligatorios
        self.fields["meta"].required = True

    def clean_valor(self):
        valor = self.cleaned_data.get("valor")
        if valor is None:
            raise forms.ValidationError("El valor es obligatorio.")
        if valor < 0:
            raise forms.ValidationError("El valor no puede ser negativo.")
        return valor
