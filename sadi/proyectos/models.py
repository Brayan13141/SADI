from django.db import models
from objetivos.models import ObjetivoEstrategico
from simple_history.models import HistoricalRecords


class Proyecto(models.Model):
    clave = models.CharField(max_length=60)
    nombre = models.CharField(max_length=500)
    objetivo = models.ForeignKey(ObjetivoEstrategico, on_delete=models.RESTRICT)
    history = HistoricalRecords()

    def __str__(self):
        return self.clave

    def save(self, *args, **kwargs):
        # --- GENERAR CLAVE AUTOMÁTICA ---
        if not self.clave or self.clave.strip().upper() == "AUTO":
            # Obtenemos la clave del objetivo
            clave_objetivo = self.objetivo.programa.clave
            count = Proyecto.objects.filter(objetivo=self.objetivo).count() + 1
            nueva_clave = f"{clave_objetivo}-PRY{count}"
            # Evitar duplicados si alguien crea varios a la vez
            while Proyecto.objects.filter(clave=nueva_clave).exists():
                count += 1
                nueva_clave = f"{clave_objetivo}-PRY{count}"

            self.clave = nueva_clave

        super().save(*args, **kwargs)
