from django.db import models
from simple_history.models import HistoricalRecords


class Departamento(models.Model):
    nombre = models.CharField(max_length=150)
    departamento_superior = models.CharField(max_length=150)

    history = HistoricalRecords()

    def __str__(self):
        return self.nombre
