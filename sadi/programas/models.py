from django.db import models
from simple_history.models import HistoricalRecords


class ProgramaEstrategico(models.Model):
    clave = models.CharField(max_length=20, unique=True)
    estado = models.BooleanField(default=True, blank=False, null=False)
    nombre = models.CharField(max_length=200)
    nombre_corto = models.CharField(max_length=20)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    duracion = models.IntegerField()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.clave} - {self.nombre}"


class Ciclo(models.Model):
    activo = models.BooleanField(default=True, blank=False, null=False)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    duracion = models.IntegerField(blank=True, null=True)
    programa = models.ForeignKey(
        ProgramaEstrategico, on_delete=models.CASCADE, related_name="ciclos"
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.programa.nombre} ({self.fecha_inicio} - {self.fecha_fin})"
