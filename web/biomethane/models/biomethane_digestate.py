from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from biomethane.models import BiomethaneContract, BiomethaneProductionUnit
from core.models import Entity


class BiomethaneDigestate(models.Model):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    DIGESTATE_STATUS = [(PENDING, "PENDING"), (VALIDATED, "VALIDATED")]

    # Propriétaire du digestat
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_digestates")

    # Année de déclaration des informations
    year = models.IntegerField()

    status = models.CharField(choices=DIGESTATE_STATUS, max_length=28)

    ## Production de digestat

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
    ON_SITE = "ON_SITE"
    EXTERNAL_PLATFORM = "EXTERNAL_PLATFORM"

    COMPOSTING_LOCATIONS = [
        (ON_SITE, "Sur site"),
        (EXTERNAL_PLATFORM, "Plateforme externe"),
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
        unique_together = ["producer", "year"]
        verbose_name = "Biométhane - Digestat"
        verbose_name_plural = "Biométhane - Digestats"


@receiver(post_save, sender=BiomethaneDigestate)
@receiver(post_save, sender=BiomethaneProductionUnit)
@receiver(post_save, sender=BiomethaneContract)
def clear_digestate_fields_on_related_model_save(sender, instance, **kwargs):
    """
    Clear specific BiomethaneDigestate fields based on related model changes.

    This signal is triggered when BiomethaneDigestate, BiomethaneProductionUnit,
    or BiomethaneContract models are saved, and clears digestate fields based on:
    - Production unit digestate phase separation settings
    - Digestate valorization methods configuration
    - Spreading management methods configuration
    - Contract installation category
    """
    # Get the producer and related objects based on the sender
    if sender == BiomethaneDigestate:
        digestate_instance = instance
        producer = instance.producer
    elif sender in [BiomethaneProductionUnit, BiomethaneContract]:
        producer = instance.producer
        digestate_instance = producer.biomethane_digestates.order_by("-id").first()
    else:
        return

    if not digestate_instance:
        return

    fields_to_clear = []

    # Handle different senders with specific logic
    if sender == BiomethaneDigestate:
        # When digestate is saved, only check composting location-based field clearing
        production_unit = getattr(producer, "biomethane_production_unit", None)
        valorization_methods = production_unit.digestate_valorization_methods if production_unit else []

        if valorization_methods and BiomethaneProductionUnit.COMPOSTING in valorization_methods:
            # Clear specific fields based on location settings
            if BiomethaneDigestate.ON_SITE not in digestate_instance.composting_locations:
                fields_to_clear.append("on_site_composted_digestate_volume")

            if BiomethaneDigestate.EXTERNAL_PLATFORM not in digestate_instance.composting_locations:
                fields_to_clear.extend(
                    [
                        "external_platform_name",
                        "external_platform_digestate_volume",
                        "external_platform_department",
                        "external_platform_municipality",
                    ]
                )

    elif sender == BiomethaneProductionUnit:
        # When production unit is saved, check all production unit related fields
        production_unit = instance

        # Clear digestate production fields based on phase separation setting
        if production_unit.has_digestate_phase_separation:
            # If phase separation is enabled, clear raw digestate fields
            fields_to_clear.extend(
                [
                    "raw_digestate_tonnage_produced",
                    "raw_digestate_dry_matter_rate",
                ]
            )
        else:
            # If phase separation is disabled, clear separated phase fields
            fields_to_clear.extend(
                [
                    "solid_digestate_tonnage",
                    "liquid_digestate_quantity",
                ]
            )

        # Get valorization methods from production unit
        valorization_methods = production_unit.digestate_valorization_methods

        # Clear spreading fields if spreading is not in valorization methods
        if BiomethaneProductionUnit.SPREADING not in valorization_methods:
            fields_to_clear.append("average_spreading_valorization_distance")

        # Clear composting fields if composting is not in valorization methods
        if BiomethaneProductionUnit.COMPOSTING not in valorization_methods:
            fields_to_clear.extend(
                [
                    "external_platform_name",
                    "external_platform_digestate_volume",
                    "external_platform_department",
                    "external_platform_municipality",
                    "on_site_composted_digestate_volume",
                    "composting_locations",
                ]
            )

        # Clear incineration/landfilling fields if not in valorization methods
        if BiomethaneProductionUnit.INCINERATION_LANDFILLING not in valorization_methods:
            fields_to_clear.extend(
                [
                    "annual_eliminated_volume",
                    "incinerator_landfill_center_name",
                    "wwtp_materials_to_incineration",
                ]
            )

        # Clear sale fields if sale is not in spreading management methods
        spreading_management_methods = production_unit.spreading_management_methods
        if BiomethaneProductionUnit.SALE not in spreading_management_methods:
            fields_to_clear.extend(
                [
                    "sold_volume",
                    "acquiring_companies",
                ]
            )

    elif sender == BiomethaneContract:
        # When contract is saved, only check contract-related fields
        contract = instance

        # Clear WWTP materials field if not installation category 2
        if contract.installation_category != BiomethaneContract.INSTALLATION_CATEGORY_2:
            fields_to_clear.append("wwtp_materials_to_incineration")

    if fields_to_clear:
        # Remove duplicates while preserving order
        fields_to_clear = list(dict.fromkeys(fields_to_clear))

        update_data = {}
        for field in fields_to_clear:
            # Special case: composting_locations should be set to empty list, not None
            new_value = [] if field == "composting_locations" else None
            update_data[field] = new_value

        BiomethaneDigestate.objects.filter(pk=digestate_instance.pk).update(**update_data)
