from django.db import models
from proyectos.models import Proyecto
from programas.models import Ciclo, ProgramaEstrategico
from departamentos.models import Departamento
from simple_history.models import HistoricalRecords


class Meta(models.Model):
    nombre = models.CharField(max_length=250, blank=True, null=True)
    clave = models.CharField(max_length=50, unique=True, blank=False, null=False)
    enunciado = models.TextField(blank=False, null=False)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.RESTRICT)
    departamento = models.ForeignKey(
        Departamento, on_delete=models.RESTRICT, null=True, blank=True
    )
    indicador = models.TextField(blank=False, null=False)
    unidadMedida = models.TextField(blank=False, null=False)
    porcentages = models.BooleanField(default=False)
    activa = models.BooleanField(default=False)
    metodoCalculo = models.TextField(blank=False, null=False)
    lineabase = models.DecimalField(
        max_digits=11, decimal_places=4, blank=True, null=True
    )
    metacumplir = models.DecimalField(
        max_digits=11, decimal_places=4, blank=True, null=True
    )
    variableB = models.DecimalField(
        max_digits=11, decimal_places=4, blank=True, null=True
    )
    ciclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE, blank=True, null=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.clave


class AvanceMeta(models.Model):
    avance = models.DecimalField(max_digits=11, decimal_places=4, blank=True, null=True)
    fecha_registro = models.DateField(blank=False, null=False)
    metaCumplir = models.ForeignKey(
        Meta, on_delete=models.RESTRICT, blank=True, null=True
    )
    departamento = models.ForeignKey(
        Departamento, on_delete=models.RESTRICT, null=True, blank=True
    )
    history = HistoricalRecords()


class MetaComprometida(models.Model):
    valor = models.DecimalField(max_digits=11, decimal_places=4, blank=True, null=True)
    meta = models.ForeignKey(Meta, on_delete=models.RESTRICT, blank=True, null=True)

    history = HistoricalRecords()
