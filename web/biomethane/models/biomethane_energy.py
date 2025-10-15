from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from biomethane.models import BiomethaneContract, BiomethaneProductionUnit
from core.models import Entity


class BiomethaneEnergy(models.Model):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    ENERGY_STATUS = [(PENDING, "PENDING"), (VALIDATED, "VALIDATED")]

    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="biomethane_energies")

    # Année de déclaration des informations
    year = models.IntegerField()

    status = models.CharField(choices=ENERGY_STATUS, max_length=28, default=PENDING)

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

    ## Nature de l'énergie utilisée pour les besoins de l'installation

    # Besoins en énergie liés au chauffage du digesteur pour une installation de méthanisation
    # ainsi qu’à l’épuration du biogaz et à l’oxydation des évents
    # J'atteste que les besoins en énergie cités ci-dessus ne sont pas satisfaits par une énergie d’origine fossile.
    attest_no_fossil_for_digester_heating_and_purification = models.BooleanField(default=False)

    # Énergie utilisée pour le chauffage du digesteur
    energy_used_for_digester_heating = models.CharField(max_length=255, null=True, blank=True)

    # Précisions (si utilisation d’énergie d’origine fossile)
    fossil_details_for_digester_heating = models.TextField(null=True, blank=True)

    # Besoins en énergie de l’installation de production de biométhane (notamment liés à la pasteurisation, l’hygiénisation
    # et le prétraitement des intrants, le chauffage du digesteur et l’épuration du biogaz)
    # J'atteste que les besoins en énergie cités ci-dessus ont pas satisfaits par une énergie d’origine fossile.
    attest_no_fossil_for_installation_needs = models.BooleanField(default=False)

    # Énergie utilisée pour la pasteurisation, l'hygiénisation et le prétraitement des intrants,
    # le chauffage du digesteur et l’épuration du biogaz
    energy_used_for_installation_needs = models.CharField(max_length=255, null=True, blank=True)

    # Précisions (si utilisation d’énergie d’origine fossile)
    fossil_details_for_installation_needs = models.TextField(null=True, blank=True)

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
    butane_or_propane_addition = models.FloatField(null=True, blank=True)

    # Quantité de combustible fossile consommé (kWh)
    fossil_fuel_consumed_kwh = models.FloatField(null=True, blank=True)

    ## Acceptabilité

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

    # Types de dysfonctionnement
    malfunction_types = models.CharField(max_length=32, choices=MALFUNCTION_TYPES, null=True, blank=True)

    # Précisions sur les dysfonctionnements
    malfunction_details = models.TextField(null=True, blank=True)

    # Difficultés pour l'injection dans le réseau de gaz en raison de périodes de saturation des réseaux
    has_injection_difficulties_due_to_network_saturation = models.BooleanField(default=False)

    # Nombre d'heures d'impossibilité d'injection (h)
    injection_impossibility_hours = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "biomethane_energy"
        unique_together = ["producer", "year"]
        verbose_name = "Biométhane - Énergie"


@receiver(post_save, sender=BiomethaneEnergy)
@receiver(post_save, sender=BiomethaneProductionUnit)
@receiver(post_save, sender=BiomethaneContract)
def clear_energy_fields_on_related_model_save(sender, instance, **kwargs):
    """
    Clear specific BiomethaneEnergy fields based on related model changes.

    This signal is triggered when BiomethaneEnergy, BiomethaneProductionUnit,
    or BiomethaneContract models are saved, and clears energy fields that
    should be reset based on the configuration changes.
    """
    # Get the producer and related objects based on the sender
    if sender == BiomethaneEnergy:
        energy_instance = instance
        producer = instance.producer
    elif sender == BiomethaneProductionUnit:
        producer = instance.producer
        energy_instance = producer.biomethane_energies.order_by("-id").first()
    elif sender == BiomethaneContract:
        producer = instance.producer
        energy_instance = producer.biomethane_energies.order_by("-id").first()
    else:
        return

    if not energy_instance:
        return

    # Get related objects
    production_unit = getattr(producer, "biomethane_production_unit", None)
    contract = getattr(producer, "biomethane_contract", None)

    fields_to_clear = []

    if sender == BiomethaneProductionUnit:
        # Clear flaring_operating_hours if FLARING_FLOWMETER is NOT in installed_meters
        if (
            production_unit
            and production_unit.installed_meters
            and BiomethaneProductionUnit.FLARING_FLOWMETER not in production_unit.installed_meters
        ):
            fields_to_clear.append("flaring_operating_hours")
    elif sender == BiomethaneContract:
        # Clear fields based on tariff reference (older tariffs)
        if contract and contract.tariff_reference not in ["2011", "2020", "2021"]:
            fields_to_clear.extend(
                [
                    "energy_used_for_digester_heating",
                    "purified_biogas_quantity_nm3",
                    "purification_electric_consumption_kwe",
                ]
            )

        # Clear fields based on tariff reference (newer tariffs)
        if contract and contract.tariff_reference not in ["2023"]:
            fields_to_clear.extend(
                [
                    "energy_used_for_installation_needs",
                    "self_consumed_biogas_nm3",
                    "total_unit_electric_consumption_kwe",
                ]
            )
    elif sender == BiomethaneEnergy:
        # Clear malfunction_details if malfunction_types is not OTHER
        if (
            energy_instance.malfunction_types
            and energy_instance.malfunction_types != BiomethaneEnergy.MALFUNCTION_TYPE_OTHER
        ):
            fields_to_clear.append("malfunction_details")

        # Clear malfunction fields if has_malfunctions is False
        if not energy_instance.has_malfunctions:
            fields_to_clear.extend(
                [
                    "malfunction_cumulative_duration_days",
                    "malfunction_types",
                    "malfunction_details",
                ]
            )

        # Clear injection_impossibility_hours if has_injection_difficulties_due_to_network_saturation is False
        if not energy_instance.has_injection_difficulties_due_to_network_saturation:
            fields_to_clear.append("injection_impossibility_hours")

    if fields_to_clear:
        update_data = {field: None for field in fields_to_clear}
        BiomethaneEnergy.objects.filter(pk=energy_instance.pk).update(**update_data)
