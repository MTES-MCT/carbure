from django.db import models
from django.db.models import Q


class Material(models.Model):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=64, unique=True)
    lhv = models.DecimalField(
        verbose_name="PCI (MJ/kg)",
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
    )
    density = models.DecimalField(
        verbose_name="Masse volumique (kg/l)",
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "material"
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(lhv__isnull=True) | Q(lhv__gt=0),
                name="material_lhv_null_or_positive",
            ),
            models.CheckConstraint(
                condition=Q(density__isnull=True) | Q(density__gt=0),
                name="material_density_null_or_positive",
            ),
        ]
