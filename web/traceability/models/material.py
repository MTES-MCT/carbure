from django.db import models
from django.db.models import Q


class Material(models.Model):
    code = models.CharField(max_length=16, unique=True)
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

    # Duplicated from Entity.UNIT_CHOICE: sharing is impractical (different contexts).
    L = "l"
    KG = "kg"
    MJ = "MJ"
    MATERIAL_UNIT_CHOICE = ((L, "litres"), (KG, "kg"), (MJ, "MJ"))
    unit = models.CharField(verbose_name="Unité", choices=MATERIAL_UNIT_CHOICE, max_length=8)

    VALORIZED_ENERGY_CODE = "VALORIZED-ENERGY"
    VALORIZED_ENERGY_NAME = "VALORIZED_ENERGY"

    @classmethod
    def valorized_energy(cls):
        """Shared MJ material assigned to VALORIZE actions. Created by load_materials."""
        return cls.objects.get(code=cls.VALORIZED_ENERGY_CODE)

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
