from django.db import models

from core.models import Entity


class BiomethaneDigestate(models.Model):
    DIGESTATE_STATUS = [
        ("PENDING", "PENDING"),
        ("VALIDATED", "VALIDATED"),
    ]

    # Propriétaire du digestat
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_digestates")

    # Année de déclaration des informations
    year = models.IntegerField()

    status = models.CharField(choices=DIGESTATE_STATUS, max_length=28)

    ## Site d'injection

    # Tonnage digestat brut produit (t)
    raw_digestate_tonnage_produced = models.FloatField(null=True, blank=True)
    # Taux de MS du digestat brut
    raw_digestate_dry_matter_rate = models.FloatField(null=True, blank=True)
    # Tonnage de digestat solide (t)
    solid_digestate_tonnage = models.FloatField(null=True, blank=True)
    # Quantité digestat liquide (en m3)
    liquid_digestate_quantity = models.FloatField(null=True, blank=True)
    # Distance moyenne de valorisation d'épandage (km)
    average_spreading_valorization_distance = models.FloatField(null=True, blank=True)

    ## Compostage
    COMPOSTING_LOCATIONS = [
        ("ON_SITE", "Sur site"),
        ("EXTERNAL_PLATFORM", "Plateforme externe"),
    ]
    # Lieux de compostage
    composting_locations = models.JSONField(default=list)
    # Nom de la plateforme externe
    external_platform_name = models.CharField(max_length=255, null=True, blank=True)
    # Volume de digestat composté sur la plateforme externe (t)
    external_platform_digestate_volume = models.FloatField(null=True, blank=True)
    # Département de la plateforme externe
    external_platform_department = models.CharField(max_length=3, null=True, blank=True)
    # Commune de la plateforme externe
    external_platform_municipality = models.CharField(max_length=255, null=True, blank=True)
    # Volume de digestat composté sur site (t)
    on_site_composted_digestate_volume = models.FloatField(null=True, blank=True)

    ## Incinération / Enfouissement

    # Volume annuel éliminé (tonnes)
    annual_eliminated_volume = models.FloatField(null=True, blank=True)
    # Nom de l'incinérateur ou du centre d'enfouissement
    incinerator_landfill_center_name = models.CharField(max_length=255, null=True, blank=True)
    # Quantité de matières totales traitées par la STEP allant en incinération (tonnes)
    wwtp_materials_to_incineration = models.FloatField(null=True, blank=True)

    ## Vente

    # Entreprise(s) acquérant le digestat
    acquiring_companies = models.TextField(null=True, blank=True)
    # Volume vendu (tonnes)
    sold_volume = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "biomethane_digestate"
        verbose_name = "Digestat"
