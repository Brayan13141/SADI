from django.db import models
from metas.models import Meta
from departamentos.models import Departamento
from usuarios.models import Usuario
from simple_history.models import HistoricalRecords


class Actividad(models.Model):
    estado = models.BooleanField(default=False)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    editable = models.BooleanField(default=True)
    meta = models.ForeignKey(Meta, on_delete=models.RESTRICT)
    responsable = models.ForeignKey(Usuario, on_delete=models.RESTRICT)
    departamento = models.ForeignKey(
        Departamento, on_delete=models.RESTRICT, null=True, blank=True
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.descripcion


class Evidencia(models.Model):
    actividad = models.ForeignKey(
        Actividad, related_name="evidencias", on_delete=models.CASCADE
    )
    archivo = models.FileField(upload_to="actividades/evidencias/")
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Bloquear edición si ya existe
        if self.pk:
            old = Evidencia.objects.get(pk=self.pk)
            if old.archivo != self.archivo:
                raise ValueError("No se puede modificar un archivo existente.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.archivo.name}"


class SolicitudReapertura(models.Model):
    actividad = models.ForeignKey("Actividad", on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    departamento = models.ForeignKey(
        "departamentos.Departamento", on_delete=models.SET_NULL, null=True
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    aprobada = models.BooleanField(default=False)

    def __str__(self):
        return f"Solicitud de {self.usuario.username} para {self.actividad.descripcion}"
