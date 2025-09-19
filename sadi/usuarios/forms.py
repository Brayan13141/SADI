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
            "role": forms.Select(attrs={"class": "form-select", "required": True}),
            "departamento": forms.Select(
                attrs={"class": "form-select", "required": True}
            ),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data["password"])  # encripta
        if commit:
            usuario.save()
        return usuario

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("El correo es obligatorio.")
        return email


class UsuarioEditForm(forms.ModelForm):
    password = forms.CharField(
        required=False,  # 👈 en edición puede ir vacío
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Contraseña (dejar en blanco para mantener la actual)",
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
        ]

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if self.cleaned_data.get("password"):  # solo si escribieron algo
            usuario.set_password(self.cleaned_data["password"])
        if commit:
            usuario.save()
        return usuario
