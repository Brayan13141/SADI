from django.db import models
from simple_history.models import HistoricalRecords


class Departamento(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.nombre
