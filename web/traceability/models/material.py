from django.db import models
from django.db.models import Q


class ActiveMaterialManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Material(models.Model):
    objects = models.Manager()
    active = ActiveMaterialManager()

    code = models.CharField(verbose_name="Code", max_length=16, unique=True)
    name = models.CharField(verbose_name="Nom", max_length=128, unique=True)
    is_active = models.BooleanField(verbose_name="Active", default=True)
    description = models.CharField(verbose_name="Description", max_length=512, blank=True, default="")
    classification = models.ForeignKey(
        "feedstocks.Classification", verbose_name="Classification", on_delete=models.SET_NULL, null=True, blank=True
    )
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
