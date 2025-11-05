from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from biomethane.models import BiomethaneContract, BiomethaneProductionUnit
from core.models import Entity


class BiomethaneDigestate(models.Model):
    # Propriétaire du digestat
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_digestates")

    # Année de déclaration des informations
    year = models.IntegerField()

    ## Production de digestat

    # Tonnage digestat brut produit (t)
    raw_digestate_tonnage_produced = models.FloatField(null=True, blank=True)
    # Taux de MS du digestat brut
    raw_digestate_dry_matter_rate = models.FloatField(null=True, blank=True)
    # Tonnage de digestat solide (t)
    solid_digestate_tonnage = models.FloatField(null=True, blank=True)
    # Quantité digestat liquide (t)
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

    @property
    def production_unit(self):
        return getattr(self.producer, "biomethane_production_unit", None)

    @property
    def optional_fields(self):
        from biomethane.services import BiomethaneDigestateService

        return BiomethaneDigestateService.get_optional_fields(self)


@receiver(post_save, sender=BiomethaneDigestate)
@receiver(post_save, sender=BiomethaneProductionUnit)
@receiver(post_save, sender=BiomethaneContract)
def clear_digestate_fields_on_related_model_save(sender, instance, **kwargs):
    """
    Clear specific BiomethaneDigestate fields based on related model changes.

    This signal is triggered when BiomethaneDigestate, BiomethaneProductionUnit,
    or BiomethaneContract models are saved, and clears digestate fields based on
    the business rules centralized in BiomethaneDigestateService.
    """
    from biomethane.services import BiomethaneDigestateService

    # Get the producer and related objects based on the sender
    if sender == BiomethaneDigestate:
        digestate_instance = instance
    elif sender in [BiomethaneProductionUnit, BiomethaneContract]:
        producer = instance.producer
        digestate_instance = producer.biomethane_digestates.order_by("-year").first()
    else:
        return

    if not digestate_instance:
        return

    # Use the service to determine which fields should be cleared
    fields_to_clear = BiomethaneDigestateService.get_fields_to_clear(digestate_instance)

    if fields_to_clear:
        # Remove duplicates while preserving order
        fields_to_clear = list(dict.fromkeys(fields_to_clear))

        update_data = {}
        for field in fields_to_clear:
            # Special case: composting_locations should be set to empty list, not None
            new_value = [] if field == "composting_locations" else None
            update_data[field] = new_value

        BiomethaneDigestate.objects.filter(pk=digestate_instance.pk).update(**update_data)
