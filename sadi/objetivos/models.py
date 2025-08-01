from django.db import models
from programas.models import ProgramaEstrategico
from simple_history.models import HistoricalRecords


class ObjetivoEstrategico(models.Model):
    clave = models.CharField(max_length=30, unique=True)
    nombre = models.TextField()
    programa = models.ForeignKey(ProgramaEstrategico, on_delete=models.RESTRICT)

    history = HistoricalRecords()

    def __str__(self):
        return self.clave
