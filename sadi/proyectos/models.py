from django.db import models
from objetivos.models import ObjetivoEstrategico
from simple_history.models import HistoricalRecords


class Proyecto(models.Model):
    clave = models.CharField(max_length=60)
    nombre = models.CharField(max_length=150)
    objetivo = models.ForeignKey(ObjetivoEstrategico, on_delete=models.RESTRICT)

    history = HistoricalRecords()

    def __str__(self):
        return self.clave
