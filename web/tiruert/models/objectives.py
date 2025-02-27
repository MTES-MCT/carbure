from django.db import models

from core.models import MatierePremiere
from tiruert.models import FossilFuelCategory


class Objective(models.Model):
    MAIN = "MAIN"
    SECTOR = "SECTOR"
    BIOFUEL_CATEGORY = "BIOFUEL_CATEGORY"
    OBJECTIVE_TYPES = ((MAIN, MAIN), (SECTOR, SECTOR), (BIOFUEL_CATEGORY, BIOFUEL_CATEGORY))

    type = models.CharField(max_length=255, choices=OBJECTIVE_TYPES)
    fuel_category = models.ForeignKey(FossilFuelCategory, on_delete=models.SET_NULL, related_name="fossil_fuels")
    customs_category = models.CharField(max_length=20, choices=MatierePremiere.MP_CATEGORIES, default=MatierePremiere.CONV)
    year = models.IntegerField()
    consideration_rate = models.FloatField()
    target = models.FloatField()

    def __str__(self):
        return f"{self.type} - {self.year} - {self.target}"

    class Meta:
        db_table = "tiruert_objectives"
        verbose_name = "Objectif Tiruert"
        verbose_name_plural = "Objectifs Tiruert"
