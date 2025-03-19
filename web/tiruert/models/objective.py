from django.db import models

from core.models import MatierePremiere


class ObjectiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("fuel_category")


class Objective(models.Model):
    MAIN = "MAIN"
    SECTOR = "SECTOR"
    BIOFUEL_CATEGORY = "BIOFUEL_CATEGORY"
    OBJECTIVE_TYPES = ((MAIN, MAIN), (SECTOR, SECTOR), (BIOFUEL_CATEGORY, BIOFUEL_CATEGORY))

    REACH = "REACH"
    CAP = "CAP"
    TARGET_TYPES = ((REACH, "Objectif à atteindre"), (CAP, "Plafond à ne pas dépasser"))

    type = models.CharField(max_length=255, choices=OBJECTIVE_TYPES)
    fuel_category = models.ForeignKey(
        "tiruert.FossilFuelCategory", null=True, on_delete=models.SET_NULL, related_name="objective_fossil_fuels", blank=True
    )
    customs_category = models.CharField(max_length=20, choices=MatierePremiere.MP_CATEGORIES, blank=True)
    year = models.IntegerField()
    consideration_rate = models.FloatField(blank=True, null=True)
    target = models.FloatField()
    target_type = models.CharField(max_length=255, choices=TARGET_TYPES, default="REACH")

    objects = ObjectiveManager()

    def __str__(self):
        return f"{self.type} - {self.year} - {self.target}"

    class Meta:
        db_table = "tiruert_objectives"
        verbose_name = "Objectif Tiruert"
        verbose_name_plural = "Objectifs Tiruert"
