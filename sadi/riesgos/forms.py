from django import forms
from django.utils import timezone
from .models import Riesgo, Mitigacion
from actividades.models import Actividad
from usuarios.models import Usuario


class RiesgoForm(forms.ModelForm):
    class Meta:
        model = Riesgo
        fields = ["enunciado", "probabilidad", "impacto", "actividad"]
        widgets = {
            "enunciado": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "probabilidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "min": 1,
                    "max": 10,
                    "onchange": "calcularRiesgo()",
                }
            ),
            "impacto": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                    "min": 1,
                    "max": 10,
                    "onchange": "calcularRiesgo()",
                }
            ),
            "actividad": forms.Select(attrs={"class": "form-select", "required": True}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        ciclo_id = kwargs.pop(
            "ciclo_id", None
        )  #  recibimos el ciclo actual desde la sesión
        super().__init__(*args, **kwargs)

        # Filtrado dinámico de actividades
        if user:
            if user.role == "DOCENTE":
                queryset = Actividad.objects.filter(departamento=user.departamento)
                if ciclo_id:  # Si hay ciclo activo en sesión, filtrar también por él
                    queryset = queryset.filter(ciclo_id=ciclo_id)
                self.fields["actividad"].queryset = queryset.order_by("id")

            else:
                queryset = Actividad.objects.all()
                if ciclo_id:
                    queryset = queryset.filter(ciclo_id=ciclo_id)
                self.fields["actividad"].queryset = queryset.order_by("id")


class MitigacionForm(forms.ModelForm):
    class Meta:
        model = Mitigacion
        fields = ["accion", "responsable", "fecha_accion", "riesgo"]
        widgets = {
            "accion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Describe la acción de mitigación",
                    "required": True,
                }
            ),
            "responsable": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Responsable",
                    "required": True,
                }
            ),
            "fecha_accion": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "required": True,
                    "id": "fecha_accion",
                }
            ),
            "riesgo": forms.Select(
                attrs={"class": "form-select", "required": True, "id": "Eid_riesgo"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        ciclo_id = kwargs.pop("ciclo_id", None)
        super().__init__(*args, **kwargs)

        hoy = timezone.now().date()
        self.fields["fecha_accion"].widget.attrs.update(
            {
                "min": hoy.strftime("%Y-%m-%d"),
                "value": hoy.strftime("%Y-%m-%d"),
            }
        )
        self.fields["fecha_accion"].initial = hoy

        # Filtrar los riesgos según el ciclo activo y el usuario
        queryset = Riesgo.objects.select_related("actividad")

        if user:
            if user.role == "DOCENTE":
                queryset = queryset.filter(actividad__departamento=user.departamento)
                if ciclo_id:
                    queryset = queryset.filter(actividad__ciclo_id=ciclo_id)
            else:
                if ciclo_id:
                    queryset = queryset.filter(actividad__ciclo_id=ciclo_id)

        self.fields["riesgo"].queryset = queryset.order_by("actividad__nombre", "id")
