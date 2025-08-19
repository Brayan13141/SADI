from django.db import models
from programas.models import Ciclo, ProgramaEstrategico
from simple_history.models import HistoricalRecords


class ObjetivoEstrategico(models.Model):
    descripcion = models.TextField()
    ciclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE, related_name="objetivos")
    programa = models.ForeignKey(
        ProgramaEstrategico, on_delete=models.CASCADE, related_name="objetivos"
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.descripcion[:50]
