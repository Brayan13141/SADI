from django import forms


from .models import Usuario
from departamentos.models import Departamento


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=True,
        label="Contraseña",
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "departamento",
            "is_active",
            "password",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "required": True}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "role": forms.Select(attrs={"class": "form-select", "required": True}),
            "departamento": forms.Select(
                attrs={"class": "form-select", "required": False}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar solo departamentos que no tienen usuario asignado
        usados = Usuario.objects.exclude(departamento__isnull=True).values_list(
            "departamento_id", flat=True
        )
        self.fields["departamento"].queryset = Departamento.objects.exclude(
            id__in=usados
        )

    def clean_departamento(self):
        departamento = self.cleaned_data.get("departamento")
        if departamento and Usuario.objects.filter(departamento=departamento).exists():
            raise forms.ValidationError(
                "Ya existe un usuario asignado a este departamento."
            )
        return departamento

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario


class UsuarioEditForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Contraseña (dejar en blanco para mantener la actual)",
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "role",
            "departamento",
            "password",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "required": True}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "required": True}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "role": forms.Select(attrs={"class": "form-select", "required": True}),
            "departamento": forms.Select(
                attrs={"class": "form-select", "required": False}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["departamento"].queryset = Departamento.objects.all()

    def clean_departamento(self):
        departamento = self.cleaned_data.get("departamento")
        if (
            departamento
            and Usuario.objects.filter(departamento=departamento)
            .exclude(id=self.instance.id)
            .exists()
        ):
            raise forms.ValidationError(
                "Ya existe un usuario asignado a este departamento."
            )
        return departamento

    def save(self, commit=True):
        usuario = super().save(commit=False)

        # Mantener contraseña anterior si no se ingresa una nueva
        nueva_pass = self.cleaned_data.get("password")
        if nueva_pass:
            usuario.set_password(nueva_pass)
        else:
            usuario.password = Usuario.objects.get(pk=self.instance.pk).password

        if commit:
            usuario.save()
        return usuario
