from django.db import models

from core.models import Pays

from .biomethane_supply_plan import BiomethaneSupplyPlan


class BiomethaneSupplyInput(models.Model):
    translation_model_key = "supply_input"
    # Plan d'approvisionnement associé
    supply_plan = models.ForeignKey(BiomethaneSupplyPlan, on_delete=models.CASCADE, related_name="supply_inputs")

    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    SOURCE_CHOICES = [
        (INTERNAL, "Interne"),
        (EXTERNAL, "Externe"),
    ]
    source = models.CharField(verbose_name="Provenance", max_length=10, choices=SOURCE_CHOICES, null=True, blank=True)

    # Intrant (matière première)
    feedstock = models.ForeignKey("core.MatierePremiere", verbose_name="Intrant", null=True, on_delete=models.PROTECT)

    # Type de CIVE (obligatoire si feedstock en catégorie CIVE)
    SUMMER = "SUMMER"
    WINTER = "WINTER"
    TYPE_CIVE_CHOICES = [
        (SUMMER, "Été"),
        (WINTER, "Hiver"),
    ]
    type_cive = models.CharField(
        verbose_name="Type de CIVE", max_length=10, choices=TYPE_CIVE_CHOICES, null=True, blank=True
    )

    # Détails culture (obligatoire pour certains codes intrant)
    culture_details = models.CharField(verbose_name="Précisez la culture", max_length=255, null=True, blank=True)

    # Type de collecte (obligatoire pour certains intrants déchets)
    PRIVATE = "PRIVATE"
    LOCAL = "LOCAL"
    IAA = "IAA"
    COLLECTION_TYPE_CHOICES = [
        (PRIVATE, "Issus de collecteurs privés"),
        (LOCAL, "Issus de collectivités locales"),
        (IAA, "Issus de résidus d'IAA"),
    ]
    collection_type = models.CharField(
        verbose_name="Type de collecte", max_length=10, choices=COLLECTION_TYPE_CHOICES, null=True, blank=True
    )

    # Unité matière
    DRY = "DRY"
    WET = "WET"

    MATERIAL_UNIT_CHOICES = [
        (DRY, "Sèche"),
        (WET, "Brute"),
    ]

    material_unit = models.CharField(
        verbose_name="Unité matière", max_length=5, choices=MATERIAL_UNIT_CHOICES, null=True, blank=True
    )

    # Ratio de matière sèche (%) - Que si matière sèche. tMB = tMS × 100 / ratio.
    dry_matter_ratio_percent = models.FloatField(verbose_name="Ratio de matière sèche (%)", null=True, blank=True)

    # Volume (tMB ou tMS en fonction du choix)
    volume = models.FloatField(verbose_name="Tonnage", null=True, blank=True)

    ##  Section Réception

    # Pays d'origine
    origin_country = models.ForeignKey(Pays, verbose_name="Pays d'origine", on_delete=models.PROTECT, default=1)

    # Département d'origine
    origin_department = models.CharField(verbose_name="Département d'origine", max_length=3, null=True, blank=True)

    # Distance moyenne pondérée d'approvisionnement (Km)
    average_weighted_distance_km = models.FloatField(
        verbose_name="Distance moyenne pondérée d'approvisionnement (Km)", null=True, blank=True
    )

    # Distance maximale (Km)
    maximum_distance_km = models.FloatField(verbose_name="Distance maximale (Km)", null=True, blank=True)

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
        return f"Intrant n°{self.id} - {self.feedstock} ({self.supply_plan.year})"
