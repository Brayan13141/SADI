from django.db import models
from programas.models import Ciclo, ProgramaEstrategico
from simple_history.models import HistoricalRecords


class ObjetivoEstrategico(models.Model):
    clave = models.CharField(max_length=50, unique=True, blank=True, null=True)
    descripcion = models.TextField()
    # ciclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE, related_name="objetivos")
    programa = models.ForeignKey(
        ProgramaEstrategico, on_delete=models.CASCADE, related_name="objetivos"
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.descripcion[:50]

    def save(self, *args, **kwargs):
        # --- GENERAR CLAVE AUTOMÁTICA ---
        if not self.clave:
            # Obtenemos la clave base del programa
            clave_programa = self.programa.clave
            count = (
                ObjetivoEstrategico.objects.filter(programa=self.programa).count() + 1
            )
            # Creamos la nueva clave
            self.clave = f"{clave_programa}-OBJ{count}"

        super().save(*args, **kwargs)
