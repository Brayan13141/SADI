from django.db import models
from proyectos.models import Proyecto
from usuarios.models import Usuario
from departamentos.models import Departamento
from simple_history.models import HistoricalRecords


class Meta(models.Model):
    clave = models.CharField(max_length=40, unique=True)
    enunciado = models.TextField()
    linea_base = models.IntegerField()
    proyecto = models.ForeignKey(Proyecto, on_delete=models.RESTRICT)
    responsable = models.ForeignKey(Usuario, on_delete=models.RESTRICT)
    departamento = models.ForeignKey(Departamento, on_delete=models.RESTRICT)

    history = HistoricalRecords()

    def __str__(self):
        return self.clave


class AvanceMeta(models.Model):
    avance = models.CharField(max_length=500)
    fecha_registro = models.DateField()
    meta = models.ForeignKey(Meta, on_delete=models.RESTRICT)
    responsable = models.ForeignKey(Usuario, on_delete=models.RESTRICT)

    history = HistoricalRecords()


class MetaComprometida(models.Model):
    valor = models.IntegerField()
    meta = models.ForeignKey(Meta, on_delete=models.RESTRICT)
    responsable = models.ForeignKey(Usuario, on_delete=models.RESTRICT)

    history = HistoricalRecords()
