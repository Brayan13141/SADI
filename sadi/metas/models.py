from django.db import models
from django.core.exceptions import ValidationError
from proyectos.models import Proyecto
from programas.models import Ciclo
from departamentos.models import Departamento
from django.db.models import Sum
from decimal import Decimal
from simple_history.models import HistoricalRecords


class Meta(models.Model):
    nombre = models.CharField(max_length=250, blank=True, null=True)
    clave = models.CharField(max_length=50, unique=True, blank=True, null=True)
    enunciado = models.TextField(blank=True, null=True, default="")
    proyecto = models.ForeignKey(Proyecto, on_delete=models.RESTRICT)
    departamento = models.ForeignKey(
        Departamento, on_delete=models.RESTRICT, null=True, blank=True
    )
    indicador = models.TextField(blank=False, null=False)
    acumulable = models.BooleanField(default=False)
    unidadMedida = models.TextField(blank=False, null=False)
    porcentages = models.BooleanField(default=False)
    activa = models.BooleanField(default=False)
    metodoCalculo = models.TextField(blank=False, null=False)
    variableB = models.BooleanField(default=True, verbose_name="Variable B")

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # --- GENERAR CLAVE AUTOMÁTICA ---
        if not self.clave:
            clave = self.proyecto.clave
            count = Meta.objects.filter(proyecto=self.proyecto).count() + 1
            self.clave = f"{clave}-{"META" + str(count)}"

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_avances(self):
        """
        Devuelve la suma total de todos los avances de la meta.
        Si la meta usa porcentajes, el total también se maneja como fracción (0.85 = 85%).
        """
        total = self.avancemeta_set.aggregate(suma=Sum("avance"))["suma"] or Decimal(
            "0"
        )
        return total

    @property
    def total_acumulado(self):
        """
        Devuelve el valor total acumulado según si la meta es acumulable o no.
        Si la meta es acumulable, suma todos los avances.
        Si no es acumulable, devuelve el último avance registrado.
        Si trabaja con porcentajes, multiplica por 100 para mostrar en porcentaje.
        """
        if self.acumulable:
            ultimo = self.avancemeta_set.order_by("-fecha_registro").first()
            total = (
                Decimal(ultimo.avance)
                if ultimo and ultimo.avance is not None
                else Decimal("0")
            )
        else:
            total = self.total_avances

        # Ajustar formato si la meta es porcentual
        if self.porcentages:
            total = total * Decimal("100")

        return total.quantize(Decimal("0.00"))


class AvanceMeta(models.Model):
    avance = models.DecimalField(max_digits=11, decimal_places=4, blank=True, null=True)
    fecha_registro = models.DateField(blank=False, null=False)
    metaCumplir = models.ForeignKey(
        Meta, on_delete=models.RESTRICT, blank=True, null=True
    )
    departamento = models.ForeignKey(
        Departamento, on_delete=models.RESTRICT, null=True, blank=True
    )
    ciclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE, blank=True, null=True)
    history = HistoricalRecords()

    def clean(self):
        if self.avance is not None:
            if self.avance < 0:
                raise ValidationError({"avance": "No se permiten valores negativos."})

    def save(self, *args, **kwargs):
        if (
            self.metaCumplir
            and self.metaCumplir.porcentages
            and self.avance is not None
        ):
            self.avance = self.avance / Decimal("100")
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def avance_display(self):
        if self.avance is None:
            return "-"
        if self.metaCumplir and self.metaCumplir.porcentages:
            valor = self.avance * Decimal("100")
            valor = valor.quantize(Decimal("0.00"))
            return f"{valor} %"
        else:
            valor = self.avance.quantize(Decimal("0.00"))
            return f"{valor}"

    @property
    def avance_button(self):
        if self.avance is None:
            return "-"
        if self.metaCumplir and self.metaCumplir.porcentages:
            valor = self.avance * Decimal("100")
            valor = valor.quantize(Decimal("0.00"))
            return f"{valor} %"
        else:
            valor = self.avance.quantize(Decimal("0.00"))
            return f"{valor}"

    def __str__(self):
        return f"Avance de {self.metaCumplir.clave if self.metaCumplir else 'Meta sin asignar'}"


class MetaComprometida(models.Model):
    valor = models.DecimalField(max_digits=11, decimal_places=4, blank=True, null=True)
    meta = models.ForeignKey(Meta, on_delete=models.RESTRICT, blank=True, null=True)
    ciclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE, blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ("meta", "ciclo")

    def clean(self):
        if self.valor is not None:
            if self.valor < 0:
                raise ValidationError({"valor": "No se permiten valores negativos."})
            if self.meta and self.meta.porcentages and self.valor > 100:
                raise ValidationError(
                    {
                        "valor": "No puede ser mayor a 100 cuando el meta tiene porcentajes activo."
                    }
                )

    def save(self, *args, **kwargs):
        if self.meta and self.meta.porcentages and self.valor is not None:
            self.valor = self.valor / Decimal("100")
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def valor_display(self):
        if self.valor is None:
            return "-"
        if self.meta and self.meta.porcentages:
            valor = self.valor * Decimal("100")
            valor = valor.quantize(Decimal("0.00"))
            return f"{valor} %"
        else:
            valor = self.valor.quantize(Decimal("0.00"))
            return f"{valor}"

    @property
    def valor_button(self):
        if self.valor is None:
            return "-"
        if self.meta and self.meta.porcentages:
            valor = self.valor * Decimal("100")
            valor = valor.quantize(Decimal("0.00"))
            return f"{valor} "
        else:
            valor = self.valor.quantize(Decimal("0.00"))
            return f"{valor}"

    def __str__(self):
        return f"Meta Comprometida de {self.meta.clave if self.meta else 'Sin meta'}"


class MetaCiclo(models.Model):
    """
    Define los valores específicos de una meta para un ciclo particular.
    """

    meta = models.ForeignKey(Meta, on_delete=models.CASCADE, related_name="metas_ciclo")
    ciclo = models.ForeignKey(
        Ciclo,
        on_delete=models.CASCADE,
        related_name="metas_ciclo",
        blank=True,
        null=True,
    )
    lineaBase = models.DecimalField(
        max_digits=11, decimal_places=4, blank=True, null=True
    )
    metaCumplir = models.DecimalField(
        max_digits=11, decimal_places=4, blank=True, null=True
    )

    history = HistoricalRecords()

    class Meta:
        unique_together = ("meta", "ciclo")

    def save(self, *args, **kwargs):
        if self.meta and self.meta.porcentages:
            divisor = Decimal("100")
            if self.lineaBase is not None:
                self.lineaBase = self.lineaBase / divisor
            if self.metaCumplir is not None:
                self.metaCumplir = self.metaCumplir / divisor
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def lineabase_button(self):
        if self.lineaBase is None:
            return "-"
        valor = (
            self.lineaBase * Decimal("100") if self.meta.porcentages else self.lineaBase
        )
        valor = valor.quantize(Decimal("0.00"))
        return f"{valor}"

    @property
    def lineabase_display(self):
        if self.lineaBase is None:
            return "-"
        valor = (
            self.lineaBase * Decimal("100") if self.meta.porcentages else self.lineaBase
        )
        valor = valor.quantize(Decimal("0.00"))
        return f"{valor} %" if self.meta.porcentages else f"{valor}"

    @property
    def metacumplir_display(self):
        if self.metaCumplir is None:
            return "-"
        valor = (
            self.metaCumplir * Decimal("100")
            if self.meta.porcentages
            else self.metaCumplir
        )
        valor = valor.quantize(Decimal("0.00"))
        return f"{valor} %" if self.meta.porcentages else f"{valor}"

    @property
    def metacumplir_button(self):
        if self.metaCumplir is None:
            return "-"
        valor = (
            self.metaCumplir * Decimal("100")
            if self.meta.porcentages
            else self.metaCumplir
        )
        valor = valor.quantize(Decimal("0.00"))
        return f"{valor}"
