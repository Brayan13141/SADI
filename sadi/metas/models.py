from django.db import models
from proyectos.models import Proyecto
from usuarios.models import Usuario
from departamentos.models import Departamento
from simple_history.models import HistoricalRecords


class Meta(models.Model):
    nombre = models.CharField(max_length=250, blank=True, null=True)
    clave = models.CharField(max_length=40, unique=True)
    enunciado = models.TextField()
    proyecto = models.ForeignKey(Proyecto, on_delete=models.RESTRICT)
    departamento = models.ForeignKey(
        Departamento, on_delete=models.RESTRICT, null=True, blank=True
    )
    indicador = models.TextField()
    unidadMedida = models.TextField()
    metodoCalculo = models.TextField()
    lineBase = models.DecimalField(
        max_digits=11, decimal_places=4, blank=True, null=True
    )
    metaCumplir = models.DecimalField(
        max_digits=11, decimal_places=4, blank=True, null=True
    )
    variableB = models.DecimalField(
        max_digits=11, decimal_places=4, blank=True, null=True
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.clave


class AvanceMeta(models.Model):
    avance = models.DecimalField(max_digits=11, decimal_places=4, blank=True, null=True)
    fecha_registro = models.DateField()
    metaCumplir = models.ForeignKey(Meta, on_delete=models.RESTRICT)
    departamento = models.ForeignKey(
        Departamento, on_delete=models.RESTRICT, null=True, blank=True
    )
    history = HistoricalRecords()


class MetaComprometida(models.Model):
    valor = models.DecimalField(max_digits=11, decimal_places=4, blank=True, null=True)
    meta = models.ForeignKey(Meta, on_delete=models.RESTRICT)
    departamento = models.ForeignKey(
        Departamento, on_delete=models.RESTRICT, null=True, blank=True
    )

    history = HistoricalRecords()
