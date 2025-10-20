from django.db import models
from django.forms import ValidationError
from metas.models import Meta
from departamentos.models import Departamento
from usuarios.models import Usuario
from simple_history.models import HistoricalRecords


class Actividad(models.Model):
    ESTADOS = [
        ("Activa", "Activa"),
        ("En Proceso", "En Proceso"),
        ("Cumplida", "Cumplida"),
        ("No Cumplida", "No Cumplida"),
    ]

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default="Activa",
        help_text="Estado actual de la actividad",
    )
    nombre = models.CharField(
        max_length=255, null=True, blank=True, help_text="Nombre corto de la actividad"
    )
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
        return f"{self.descripcion} ({self.get_estado_display()})"


class Evidencia(models.Model):
    actividad = models.ForeignKey(
        Actividad, related_name="evidencias", on_delete=models.CASCADE
    )
    archivo = models.FileField(upload_to="actividades/evidencias/")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

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
    terminada = models.BooleanField(default=False)
    history = HistoricalRecords()

    def clean(self):
        if not self.aprobada:
            existe = (
                SolicitudReapertura.objects.filter(
                    actividad=self.actividad, aprobada=False
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if existe:
                raise ValidationError(
                    "Ya existe una solicitud pendiente para esta actividad."
                )

    def __str__(self):
        return f"Solicitud de {self.usuario.username} para {self.actividad.descripcion}"
