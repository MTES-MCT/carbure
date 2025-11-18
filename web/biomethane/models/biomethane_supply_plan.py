from django.db import models

from core.models import Entity


class BiomethaneSupplyPlan(models.Model):
    # Producteur associé au plan d'approvisionnement
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_supply_plans")

    # Année du plan d'approvisionnement
    year = models.IntegerField(verbose_name="Année")

    class Meta:
        db_table = "biomethane_supply_plan"
        verbose_name = "Plan d'approvisionnement"
        verbose_name_plural = "Plans d'approvisionnement"
        unique_together = ["producer", "year"]

    @property
    def production_unit(self):
        return getattr(self.producer, "biomethane_production_unit", None)

    def __str__(self):
        return f"Plan d'approvisionnement {self.year} - {self.producer.name}"
