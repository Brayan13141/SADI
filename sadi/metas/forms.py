from django.utils import timezone
from django import forms
from .models import Meta, AvanceMeta, MetaComprometida, MetaCiclo
from proyectos.models import Proyecto
from departamentos.models import Departamento
from programas.models import Ciclo


class AsignarCicloMetaForm(forms.ModelForm):

    class Meta:
        model = MetaCiclo
        fields = ["ciclo", "lineaBase", "metaCumplir"]

        widgets = {
            "ciclo": forms.Select(attrs={"class": "form-control"}),
            "lineaBase": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "metaCumplir": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.meta_obj = kwargs.pop("meta", None)
        super().__init__(*args, **kwargs)


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
            "variableB",
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
            "variableB": forms.CheckboxInput(attrs={"class": "form-check-input"}),
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
            "proyecto",
            "departamento",
            "indicador",
            "acumulable",
            "unidadMedida",
            "porcentages",
            "activa",
            "metodoCalculo",
        ]
        widgets = {
            "clave": forms.TextInput(attrs={"class": "form-control"}),
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "required": True}
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in [
            "clave",
            "nombre",
            "indicador",
            "unidadMedida",
            "metodoCalculo",
            "proyecto",
            "activa",
            "departamento",
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
        fields = ["avance", "fecha_registro"]
        widgets = {
            "avance": forms.NumberInput(
                attrs={"class": "form-control", "required": True, "min": "0"}
            ),
            "fecha_registro": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        # Obtener la meta desde los argumentos si está disponible
        meta = kwargs.pop("meta", None)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user.role == "DOCENTE":
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
        return avance


class MetaComprometidaForm(forms.ModelForm):
    class Meta:
        model = MetaComprometida
        fields = ["valor", "meta", "ciclo"]
        widgets = {
            "valor": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "placeholder": "Ingrese el valor comprometido",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "meta": forms.HiddenInput(),
            # ciclo ya no será oculto, lo quitamos de aquí
        }

    ciclo = forms.ModelChoiceField(
        queryset=Ciclo.objects.all().order_by("-nombre"),
        label="Ciclo",
        widget=forms.Select(attrs={"class": "form-select", "required": True}),
        empty_label="Seleccione un ciclo",
    )

    def clean_valor(self):
        valor = self.cleaned_data.get("valor")
        if valor is not None and valor < 0:
            raise forms.ValidationError("El valor no puede ser negativo.")
        return valor


# ========================FORMULARIOS DE AVANCE Y COMPROMETIDA MASIVO========================#
class AvanceMetaGeneralForm(forms.ModelForm):
    class Meta:
        model = AvanceMeta
        fields = ["avance", "fecha_registro", "metaCumplir", "departamento", "ciclo"]
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
                    "step": 0.01,
                }
            ),
            "metaCumplir": forms.Select(
                attrs={"class": "form-select", "required": True, "id": "id_metaCumplir"}
            ),
            "departamento": forms.Select(
                attrs={"class": "form-select", "id": "id_departamento"}
            ),
            "ciclo": forms.Select(attrs={"class": "form-select", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["metaCumplir"].queryset = Meta.objects.all()
        self.fields["departamento"].queryset = Departamento.objects.all()
        self.fields["ciclo"].queryset = Ciclo.objects.all()
        self.fields["departamento"].required = False  # Hacer que no sea obligatorio

    def clean_avance(self):
        avance = self.cleaned_data.get("avance")
        if avance is not None:
            if avance < 0:
                raise forms.ValidationError("El avance no puede ser negativo.")
        else:
            raise forms.ValidationError("El avance es obligatorio.")
        return avance


class MetaComprometidaGeneralForm(forms.ModelForm):
    class Meta:
        model = MetaComprometida
        fields = ["valor", "meta"]  #  quitamos ciclo del formulario visible
        widgets = {
            "valor": forms.NumberInput(
                attrs={"class": "form-control", "required": True}
            ),
            "meta": forms.Select(attrs={"class": "form-select", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        ciclo_actual = kwargs.pop(
            "ciclo_actual", None
        )  #  pasamos el ciclo desde la view
        super().__init__(*args, **kwargs)

        self.fields["meta"].queryset = Meta.objects.all().order_by("id")
        self.fields["meta"].required = True

        self.ciclo_actual = ciclo_actual

    def clean_valor(self):
        valor = self.cleaned_data.get("valor")
        if valor is None:
            raise forms.ValidationError("El valor es obligatorio.")
        if valor < 0:
            raise forms.ValidationError("El valor no puede ser negativo.")
        return valor
