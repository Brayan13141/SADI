from django.db import models
from simple_history.models import HistoricalRecords


class ProgramaEstrategico(models.Model):
    clave = models.CharField(max_length=20, unique=True)
    estado = models.BooleanField(default=True, blank=False, null=False)
    nombre = models.CharField(max_length=200)
    nombre_corto = models.CharField(max_length=20)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    duracion = models.DecimalField(max_digits=3, decimal_places=1)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.clave} - {self.nombre}"

    def save(self, *args, **kwargs):
        if self.fecha_inicio and self.fecha_fin:
            diff_days = (self.fecha_fin - self.fecha_inicio).days
            self.duracion = round(diff_days / 365.25, 1)
        super().save(*args, **kwargs)


class Ciclo(models.Model):
    ESTADOS = [
        ("Activo", "Activa"),
        ("Inactivo", "Inactivo"),
        ("En proceso", "En proceso"),
    ]

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default="Activo",
    )
    nombre = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    duracion = models.IntegerField(blank=True, null=True)
    programa = models.ForeignKey(
        ProgramaEstrategico, on_delete=models.CASCADE, related_name="ciclos"
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.programa.nombre} ({self.fecha_inicio} - {self.fecha_fin})"

    def save(self, *args, **kwargs):
        # --- Calcular duración aproximada en años ---
        if self.fecha_inicio and self.fecha_fin:
            diff_days = (self.fecha_fin - self.fecha_inicio).days
            self.duracion = round(diff_days / 365.25, 1)

        # --- Generar nombre automáticamente ---
        if self.programa and self.fecha_inicio and self.fecha_fin:
            # Tomamos el nombre corto del programa (asumiendo que el campo existe)
            nombre_corto = getattr(self.programa, "nombre_corto", None)

            # Si el programa no tiene nombre corto, usa su nombre normal
            if not nombre_corto:
                nombre_corto = self.programa.nombre

            # Asignar el nombre con el formato requerido
            self.nombre = f"{nombre_corto} - {self.fecha_inicio} - {self.fecha_fin}"

        super().save(*args, **kwargs)
