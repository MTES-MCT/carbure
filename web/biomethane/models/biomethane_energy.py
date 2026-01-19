from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from biomethane.models import BiomethaneContract, BiomethaneProductionUnit
from core.models import Entity


class BiomethaneEnergy(models.Model):
    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_energies")

    # Année de déclaration des informations
    year = models.IntegerField()

    ## Biométhane injecté dans le réseau

    # Quantité de biométhane injecté (GWhPCS/an)
    injected_biomethane_gwh_pcs_per_year = models.FloatField(null=True, blank=True)

    # Quantité de biométhane injecté (Nm3/an)
    injected_biomethane_nm3_per_year = models.FloatField(null=True, blank=True)

    # Taux de Ch4 dans le biométhane injecté (%)
    injected_biomethane_ch4_rate_percent = models.FloatField(null=True, blank=True)

    # PCS du biométhane injecté (kWh/Nm3)
    injected_biomethane_pcs_kwh_per_nm3 = models.FloatField(null=True, blank=True)

    # Nombre d'heures de fonctionnement (h)
    operating_hours = models.FloatField(null=True, blank=True)

    ## Production de biogaz

    # Quantité de biogaz produit (Nm3/an)
    produced_biogas_nm3_per_year = models.FloatField(null=True, blank=True)

    # Quantité de biogaz torché (Nm3/an)
    flared_biogas_nm3_per_year = models.FloatField(null=True, blank=True)

    # Nombre d'heures de fonctionnement de la torchère (h)
    flaring_operating_hours = models.FloatField(null=True, blank=True)

    MALFUNCTION_TYPE_CONCEPTION = "CONCEPTION"

    MALFUNCTION_TYPES = [
        (MALFUNCTION_TYPE_CONCEPTION, "Conception"),
    ]

    ## Nature de l'énergie utilisée pour les besoins de l'installation

    # Types d'énergie possibles
    ENERGY_TYPE_PRODUCED_BIOGAS = "PRODUCED_BIOGAS"
    ENERGY_TYPE_PRODUCED_BIOMETHANE = "PRODUCED_BIOMETHANE"
    ENERGY_TYPE_WASTE_HEAT_PREEXISTING = "WASTE_HEAT_PREEXISTING"
    ENERGY_TYPE_WASTE_HEAT_PURIFICATION = "WASTE_HEAT_PURIFICATION"
    ENERGY_TYPE_WASTE_HEAT_ON_SITE = "WASTE_HEAT_ON_SITE"
    ENERGY_TYPE_BIOMASS_BOILER = "BIOMASS_BOILER"
    ENERGY_TYPE_SOLAR_THERMAL = "SOLAR_THERMAL"
    ENERGY_TYPE_OTHER_RENEWABLE = "OTHER_RENEWABLE"
    ENERGY_TYPE_FOSSIL = "FOSSIL"
    ENERGY_TYPE_OTHER = "OTHER"

    ENERGY_TYPES = [
        (ENERGY_TYPE_PRODUCED_BIOGAS, "Biogaz produit par l'installation"),
        (ENERGY_TYPE_PRODUCED_BIOMETHANE, "Biométhane produit par l'installation"),
        (
            ENERGY_TYPE_WASTE_HEAT_PREEXISTING,
            "Chaleur fatale [Energie thermique résiduelle] (issue d'un équipement préexistant installé sur site "
            + "ou sur un site situé à proximité)",
        ),
        (
            ENERGY_TYPE_WASTE_HEAT_PURIFICATION,
            "Chaleur fatale (issue du système d'épuration ou de compression de l'installation)",
        ),
        (
            ENERGY_TYPE_WASTE_HEAT_ON_SITE,
            "Chaleur fatale (issue d'un équipement installé sur site)",
        ),
        (ENERGY_TYPE_BIOMASS_BOILER, "Chaudière biomasse"),
        (ENERGY_TYPE_SOLAR_THERMAL, "Solaire thermique"),
        (ENERGY_TYPE_OTHER_RENEWABLE, "Autre énergie renouvelable"),
        (ENERGY_TYPE_FOSSIL, "Energie fossile"),
        (ENERGY_TYPE_OTHER, "Autre"),
    ]

    # Besoins en énergie de l'installation de production de biométhane / au chauffage du digesteur
    attest_no_fossil_for_energy = models.BooleanField(default=False)

    # Type d'énergie utilisée pour le chauffage du digesteur
    # Type d'énergie utilisée pour la pasteurisation, l'hygiénisation et le prétraitement des intrants,
    # le chauffage du digesteur et l’épuration du biogaz
    energy_types = models.JSONField(null=True, blank=True, default=list)

    # Précisions
    energy_details = models.TextField(null=True, blank=True)

    ## Efficacité énergétique

    # Quantité totale de biogaz traitée par le système d'épuration sur l’année (Nm3)
    purified_biogas_quantity_nm3 = models.FloatField(null=True, blank=True)

    # Consommation électrique du système d'épuration et le cas échéant du traitement des évents (kWe)
    purification_electric_consumption_kwe = models.FloatField(null=True, blank=True)

    # Quantité de biogaz autoconsommée pour la pasteurisation, l'hygiénisation ou le traitement des intrants,
    # le chauffage du digesteur et l’épuration du biogaz  (Nm3)
    self_consumed_biogas_nm3 = models.FloatField(null=True, blank=True)

    # Consommation électrique soutirée pour l'ensemble de l'unité (kWe)
    total_unit_electric_consumption_kwe = models.FloatField(null=True, blank=True)

    # Addition de butane ou propane lors de l'injection du biométhane dans le réseau
    butane_or_propane_addition = models.BooleanField(default=False)

    # Quantité de combustible fossile consommé (kWh)
    fossil_fuel_consumed_kwh = models.FloatField(null=True, blank=True)

    ## Questions diverses

    # L'exploitation de votre unité de méthanisation fait-elle l'objet actuellement
    # d'une opposition ou de plaintes de voisinage ?
    has_opposition_or_complaints_acceptability = models.BooleanField(default=False)

    # Nombre de jour travail estimé pour l'activité de méthanisation sur l'année
    estimated_work_days_acceptability = models.IntegerField(null=True, blank=True)

    ## Dysfonctionnements

    # Y a-t-il eu des dysfonctionnements ?
    has_malfunctions = models.BooleanField(default=False)

    # Durée cumulée du dysfonctionnement (en jours)
    malfunction_cumulative_duration_days = models.IntegerField(null=True, blank=True)

    # Types de dysfonctionnement
    MALFUNCTION_TYPE_CONCEPTION = "CONCEPTION"
    MALFUNCTION_TYPE_MAINTENANCE = "MAINTENANCE"
    MALFUNCTION_TYPE_BIOLOGICAL = "BIOLOGICAL"
    MALFUNCTION_TYPE_ACCIDENT = "ACCIDENT"
    MALFUNCTION_TYPE_PURIFIER = "PURIFIER"
    MALFUNCTION_TYPE_INJECTION_POST = "INJECTION_POST"
    MALFUNCTION_TYPE_INPUTS = "INPUTS"
    MALFUNCTION_TYPE_OTHER = "OTHER"

    MALFUNCTION_TYPES = [
        (MALFUNCTION_TYPE_CONCEPTION, "Conception"),
        (MALFUNCTION_TYPE_MAINTENANCE, "Entretien/Maintenance"),
        (MALFUNCTION_TYPE_BIOLOGICAL, "Biologique"),
        (MALFUNCTION_TYPE_ACCIDENT, "Accident deversement"),
        (MALFUNCTION_TYPE_PURIFIER, "Épurateur"),
        (MALFUNCTION_TYPE_INJECTION_POST, "Poste d'injection (autre que problématiques de saturation des réseaux)"),
        (MALFUNCTION_TYPE_INPUTS, "Intrants"),
        (MALFUNCTION_TYPE_OTHER, "Autres (à préciser)"),
    ]

    # Types de dysfonctionnement (peut contenir plusieurs valeurs)
    malfunction_types = models.JSONField(null=True, blank=True, default=list)

    # Précisions sur les dysfonctionnements
    malfunction_details = models.TextField(null=True, blank=True)

    # Difficultés pour l'injection dans le réseau de gaz en raison de périodes de saturation des réseaux
    has_injection_difficulties_due_to_network_saturation = models.BooleanField(default=False)

    # Nombre d'heures d'impossibilité d'injection (h)
    injection_impossibility_hours = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "biomethane_energy"
        unique_together = ["producer", "year"]
        verbose_name = "Énergie"

    @property
    def production_unit(self):
        return getattr(self.producer, "biomethane_production_unit", None)

    @property
    def optional_fields(self):
        from biomethane.services import BiomethaneEnergyService

        return BiomethaneEnergyService.get_optional_fields(self)


@receiver(post_save, sender=BiomethaneEnergy)
@receiver(post_save, sender=BiomethaneProductionUnit)
@receiver(post_save, sender=BiomethaneContract)
def clear_energy_fields_on_related_model_save(sender, instance, **kwargs):
    """
    Clear specific BiomethaneEnergy fields based on related model changes.

    This signal is triggered when BiomethaneEnergy, BiomethaneProductionUnit,
    or BiomethaneContract models are saved, and clears energy fields based on
    the business rules centralized in BiomethaneEnergyService.
    """
    from biomethane.services import BiomethaneEnergyService

    # Get the producer and related objects based on the sender
    if sender == BiomethaneEnergy:
        energy_instance = instance
    elif sender in [BiomethaneProductionUnit, BiomethaneContract]:
        producer = instance.producer
        energy_instance = producer.biomethane_energies.order_by("-year").first()
    else:
        return

    if not energy_instance:
        return

    # Use the service to determine which fields should be cleared
    fields_to_clear = BiomethaneEnergyService.get_fields_to_clear(energy_instance)

    if fields_to_clear:
        update_data = {field: None for field in fields_to_clear}

        BiomethaneEnergy.objects.filter(pk=energy_instance.pk).update(**update_data)


@receiver(pre_save, sender=BiomethaneContract)
def update_energy_fields_on_contract_save(sender, instance, **kwargs):
    old_contract = sender.objects.filter(pk=instance.pk).first()

    if old_contract and (
        old_contract.tariff_reference != instance.tariff_reference
        or old_contract.installation_category != instance.installation_category
    ):
        producer = instance.producer
        energy_instance = producer.biomethane_energies.order_by("-year").first()
        if energy_instance:
            fields_to_clear = ["energy_types"]
            update_data = {field: None for field in fields_to_clear}
            BiomethaneEnergy.objects.filter(pk=energy_instance.pk).update(**update_data)
