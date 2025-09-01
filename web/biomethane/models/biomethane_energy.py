from django.db import models

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

    class Meta:
        db_table = "biomethane_energy"
        verbose_name = "Biométhane - Énergie"
