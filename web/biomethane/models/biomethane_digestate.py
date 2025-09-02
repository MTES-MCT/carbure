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
        verbose_name = "Digestat"


@receiver(post_save, sender=BiomethaneDigestate)
@receiver(post_save, sender=BiomethaneProductionUnit)
@receiver(post_save, sender=BiomethaneContract)
def clear_fields(sender, instance, **kwargs):
    fields_to_clear = []

    if sender == BiomethaneDigestate:
        digestate_instance = instance
        producer = instance.producer
        production_unit = producer.biomethane_production_unit if hasattr(producer, "biomethane_production_unit") else None
        contract = producer.biomethane_contract if hasattr(producer, "biomethane_contract") else None
    elif sender == BiomethaneProductionUnit:
        production_unit = instance
        producer = instance.producer
        digestate_instance = producer.biomethane_digestates.last()  # get the most recent one
        contract = producer.biomethane_contract if hasattr(producer, "biomethane_contract") else None
    elif sender == BiomethaneContract:
        contract = instance
        producer = contract.producer
        production_unit = producer.biomethane_production_unit if hasattr(producer, "biomethane_production_unit") else None
        digestate_instance = producer.biomethane_digestates.last()  # get the most recent one
    else:
        return

    if not digestate_instance:
        return

    ## Production de digestat
    if production_unit and production_unit.has_digestate_phase_separation:
        fields_to_clear += [
            "raw_digestate_tonnage_produced",
            "raw_digestate_dry_matter_rate",
        ]
    elif production_unit and not production_unit.has_digestate_phase_separation:
        fields_to_clear += [
            "solid_digestate_tonnage",
            "liquid_digestate_quantity",
        ]
    else:
        fields_to_clear += [
            "raw_digestate_tonnage_produced",
            "raw_digestate_dry_matter_rate",
            "solid_digestate_tonnage",
            "liquid_digestate_quantity",
        ]

    ## Epandage
    valorization_methods = production_unit.digestate_valorization_methods if production_unit else []
    if not valorization_methods or BiomethaneProductionUnit.SPREADING not in valorization_methods:
        fields_to_clear += [
            "average_spreading_valorization_distance",
        ]

    ## Compostage
    if not valorization_methods or BiomethaneProductionUnit.COMPOSTING not in valorization_methods:
        fields_to_clear += [
            "external_platform_name",
            "external_platform_digestate_volume",
            "external_platform_department",
            "external_platform_municipality",
            "on_site_composted_digestate_volume",
            "composting_locations",
        ]

    else:
        if BiomethaneDigestate.ON_SITE not in digestate_instance.composting_locations:
            fields_to_clear += [
                "on_site_composted_digestate_volume",
            ]

        if BiomethaneDigestate.EXTERNAL_PLATFORM not in digestate_instance.composting_locations:
            fields_to_clear += [
                "external_platform_name",
                "external_platform_digestate_volume",
                "external_platform_department",
                "external_platform_municipality",
            ]

    ## Incinération / Enfouissement
    if not valorization_methods or BiomethaneProductionUnit.INCINERATION_LANDFILLING not in valorization_methods:
        fields_to_clear += [
            "annual_eliminated_volume",
            "incinerator_landfill_center_name",
            "wwtp_materials_to_incineration",
        ]

    if contract is None or contract.installation_category != BiomethaneContract.INSTALLATION_CATEGORY_2:
        fields_to_clear += [
            "wwtp_materials_to_incineration",
        ]

    ## Vente
    spreading_management_methods = production_unit.spreading_management_methods if production_unit else []
    if not spreading_management_methods or BiomethaneProductionUnit.SALE not in spreading_management_methods:
        fields_to_clear += [
            "sold_volume",
            "acquiring_companies",
        ]

    if fields_to_clear:
        update_data = {}
        for field in fields_to_clear:
            new_value = None if field != "composting_locations" else {}
            update_data[field] = new_value
        BiomethaneDigestate.objects.filter(pk=digestate_instance.pk).update(**update_data)
