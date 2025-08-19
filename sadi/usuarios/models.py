from django.contrib.auth.models import AbstractUser
from django.db import models
from departamentos.models import Departamento
from simple_history.models import HistoricalRecords


class Usuario(AbstractUser):
    ROLE_CHOICES = [
        ("ADMIN", "Administrador"),
        ("APOYO", "Apoyo"),
        ("RESPONSABLE", "Responsable"),
        ("INVITADO", "Invitado"),
    ]

    role = models.CharField(max_length=15, choices=ROLE_CHOICES)
    departamento = models.ForeignKey(Departamento, on_delete=models.RESTRICT, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.username
