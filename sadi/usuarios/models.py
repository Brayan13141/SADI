from django.contrib.auth.models import AbstractUser
from django.db import models
from departamentos.models import Departamento
from simple_history.models import HistoricalRecords


class Usuario(AbstractUser):
    ROLE_CHOICES = [
        ("ADMIN", "Administrador"),
        ("APOYO", "Apoyo"),
        ("DOCENTE", "Docente"),
        ("INVITADO", "Invitado"),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    departamento = models.OneToOneField(
        Departamento, on_delete=models.RESTRICT, null=True, unique=True, blank=True
    )
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # Si es superuser y no tiene rol asignado → poner ADMIN
        if self.is_superuser and not self.role:
            self.role = "ADMIN"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
