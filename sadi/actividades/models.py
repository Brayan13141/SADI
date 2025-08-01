from django.db import models
from metas.models import Meta
from usuarios.models import Usuario
from simple_history.models import HistoricalRecords


class Actividad(models.Model):
    estado = models.BooleanField(default=False)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    evidencia = models.CharField(max_length=500, blank=True, null=True)
    meta = models.ForeignKey(Meta, on_delete=models.RESTRICT)
    responsable = models.ForeignKey(Usuario, on_delete=models.RESTRICT)

    history = HistoricalRecords()

    def __str__(self):
        return self.descripcion
