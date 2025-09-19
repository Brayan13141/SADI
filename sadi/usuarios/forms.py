from django import forms
from .models import Usuario


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
            "is_active",  # Añadido
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
            "is_active": forms.CheckboxInput(  # Añadido
                attrs={"class": "form-check-input"}
            ),
            "role": forms.Select(attrs={"class": "form-select", "required": True}),
            "departamento": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": False,
                }  # Cambiado a no requerido si es opcional
            ),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario


class UsuarioEditForm(forms.ModelForm):
    password = forms.CharField(
        required=False,  # Cambiado a False para que no sea obligatorio
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
            "is_active",  # Añadido
            "role",  # Añadido
            "departamento",  # Añadido
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
            "is_active": forms.CheckboxInput(  # Añadido
                attrs={"class": "form-check-input"}
            ),
            "role": forms.Select(attrs={"class": "form-select", "required": True}),
            "departamento": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": False,
                }  # Cambiado a no requerido si es opcional
            ),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        # Solo establecer nueva contraseña si se proporciona
        if self.cleaned_data.get("password"):
            usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario
