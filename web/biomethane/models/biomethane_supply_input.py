from django.db import models

from biomethane.models import BiomethaneSupplyPlan
from core.models import Pays


class BiomethaneSupplyInput(models.Model):
    # Plan d'approvisionnement associé
    supply_plan = models.ForeignKey(BiomethaneSupplyPlan, on_delete=models.CASCADE, related_name="supply_inputs")

    ## Section Intrant

    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"

    SOURCE_CHOICES = [
        (INTERNAL, "Interne"),
        (EXTERNAL, "Externe"),
    ]

    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)

    # Type de culture
    MAIN = "MAIN"
    INTERMEDIATE = "INTERMEDIATE"

    CROP_TYPE_CHOICES = [
        (MAIN, "Principale"),
        (INTERMEDIATE, "Intermédiaire"),
    ]

    crop_type = models.CharField(max_length=15, choices=CROP_TYPE_CHOICES)

    # Intrants
    input_name = models.ForeignKey("core.MatierePremiere", null=True, on_delete=models.PROTECT)

    # Type de CIVE (obligatoire si input_name.code == "Seigle - CIVE")
    SUMMER = "SUMMER"
    WINTER = "WINTER"
    TYPE_CIVE_CHOICES = [
        (SUMMER, "Été"),
        (WINTER, "Hiver"),
    ]
    type_cive = models.CharField(max_length=10, choices=TYPE_CIVE_CHOICES, null=True, blank=True)

    # Détails culture (obligatoire si input_name.code == "Autres cultures")
    culture_details = models.CharField(max_length=255, null=True, blank=True)

    # Unité matière
    DRY = "DRY"
    WET = "WET"

    MATERIAL_UNIT_CHOICES = [
        (DRY, "Sèche"),
        (WET, "Brute"),
    ]

    material_unit = models.CharField(max_length=5, choices=MATERIAL_UNIT_CHOICES)

    # Ratio de matière sèche (%) - Que si matière sèche
    dry_matter_ratio_percent = models.FloatField(null=True, blank=True)

    # Volume (tMB ou tMS en fonction du choix)
    volume = models.FloatField()

    ##  Section Réception

    # Pays d'origine
    origin_country = models.ForeignKey(Pays, on_delete=models.PROTECT, default=1)

    # Département d'origine
    origin_department = models.CharField(max_length=3, null=True, blank=True)

    # Distance moyenne pondérée d'approvisionnement (Km)
    average_weighted_distance_km = models.FloatField(null=True, blank=True)

    # Distance maximale (Km)
    maximum_distance_km = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "biomethane_supply_input"
        verbose_name = "Intrant d'approvisionnement"
        verbose_name_plural = "Intrants d'approvisionnement"
        ordering = ["supply_plan", "id"]

    @property
    def production_unit(self):
        if hasattr(self, "supply_plan") and self.supply_plan:
            return getattr(self.supply_plan.producer, "biomethane_production_unit", None)
        return None

    def __str__(self):
        return f"Intrant n°{self.id} - {self.input_name} ({self.supply_plan.year})"
