from django.db import models
from actividades.models import Actividad
from usuarios.models import Usuario
from simple_history.models import HistoricalRecords


class Riesgo(models.Model):
    enunciado = models.CharField(max_length=200)
    probabilidad = models.IntegerField()
    impacto = models.IntegerField()
    riesgo = models.IntegerField(default=0)
    actividad = models.ForeignKey(
        Actividad, on_delete=models.RESTRICT, null=True, blank=True
    )

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.riesgo = self.probabilidad * self.impacto
        super().save(*args, **kwargs)

    def __str__(self):
        return self.enunciado


class Mitigacion(models.Model):
    accion = models.CharField(max_length=250)
    fecha_accion = models.DateField()
    responsable = models.ForeignKey(Usuario, on_delete=models.RESTRICT)
    riesgo = models.ForeignKey(Riesgo, on_delete=models.RESTRICT)

    history = HistoricalRecords()

    def __str__(self):
        return self.accion
