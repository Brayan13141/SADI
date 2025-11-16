from django.db import models


class ConfiguracionGlobal(models.Model):
    captura_activa = models.BooleanField(default=True)

    def __str__(self):
        return "Configuración Global"
