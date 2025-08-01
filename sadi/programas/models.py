from django.db import models
from simple_history.models import HistoricalRecords


class ProgramaEstrategico(models.Model):
    clave = models.CharField(max_length=20, unique=True)
    estado = models.BooleanField(default=False)
    nombre = models.CharField(max_length=200)
    nombre_corto = models.CharField(max_length=20)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    duracion = models.IntegerField()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.clave} - {self.nombre}"
