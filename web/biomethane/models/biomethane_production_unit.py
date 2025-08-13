from django.db import models

from core.models import Entity


class BiomethaneProductionUnit(models.Model):
    # Propriétaire de l'unité de production
    producer = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name="biomethane_production_unit")

    # Nom de l'unité
    unit_name = models.CharField(max_length=128)

    # SIRET
    siret_number = models.CharField(max_length=16, null=True, blank=True)

    # Adresse de la société
    company_address = models.CharField(max_length=256, null=True, blank=True)

    # légende
    AGRICULTURAL_AUTONOMOUS = "AGRICULTURAL_AUTONOMOUS"
    AGRICULTURAL_TERRITORIAL = "AGRICULTURAL_TERRITORIAL"
    INDUSTRIAL_TERRITORIAL = "INDUSTRIAL_TERRITORIAL"
    HOUSEHOLD_WASTE_BIOWASTE = "HOUSEHOLD_WASTE_BIOWASTE"
    ISDND = "ISDND"

    unit_type = models.CharField(
        max_length=32,
        choices=[
            (AGRICULTURAL_AUTONOMOUS, "Agricole autonome"),
            (AGRICULTURAL_TERRITORIAL, "Agricole territorial"),
            (INDUSTRIAL_TERRITORIAL, "Industriel territorial"),
            (HOUSEHOLD_WASTE_BIOWASTE, "Déchets ménagers et biodéchets"),
            (ISDND, "ISDND"),
        ],
        null=True,
        blank=True,
    )

    # Votre site dispose-t-il d’un agrément sanitaire ?
    has_sanitary_approval = models.BooleanField(default=False)

    # N˚ agrément sanitaire
    sanitary_approval_number = models.CharField(max_length=32, null=True, blank=True)

    # Disposez vous d’une dérogation à l’hygiénisation?
    has_hygienization_exemption = models.BooleanField(default=False)

    # Dérogation à l'hygiénisation
    TOTAL = "TOTAL"
    PARTIAL = "PARTIAL"

    hygienization_exemption_type = models.CharField(
        max_length=16,
        choices=[
            (TOTAL, "Totale"),
            (PARTIAL, "Partielle"),
        ],
        null=True,
        blank=True,
    )

    # N˚ ICPE
    icpe_number = models.CharField(max_length=32, null=True, blank=True)

    # Régime ICPE
    AUTHORIZATION = "AUTHORIZATION"
    REGISTRATION = "REGISTRATION"
    DECLARATION_PERIODIC_CONTROLS = "DECLARATION_PERIODIC_CONTROLS"

    icpe_regime = models.CharField(
        max_length=32,
        choices=[
            (AUTHORIZATION, "Autorisation"),
            (REGISTRATION, "Enregistrement"),
            (DECLARATION_PERIODIC_CONTROLS, "Déclaration (avec contrôles périodiques)"),
        ],
        null=True,
        blank=True,
    )

    # Type de voie
    LIQUID_PROCESS = "LIQUID_PROCESS"
    DRY_PROCESS = "DRY_PROCESS"

    process_type = models.CharField(
        max_length=16,
        choices=[
            (LIQUID_PROCESS, "Voie liquide"),
            (DRY_PROCESS, "Voie sèche"),
        ],
        null=True,
        blank=True,
    )

    # Procédé méthanisation
    CONTINUOUS_INFINITELY_MIXED = "CONTINUOUS_INFINITELY_MIXED"  # Continu (infiniment mélangé)
    PLUG_FLOW_SEMI_CONTINUOUS = "PLUG_FLOW_SEMI_CONTINUOUS"  # En piston (semi-continu)
    BATCH_SILOS = "BATCH_SILOS"  # En silos (batch)

    methanization_process = models.CharField(
        max_length=32,
        choices=[
            (CONTINUOUS_INFINITELY_MIXED, "Continu (infiniment mélangé)"),
            (PLUG_FLOW_SEMI_CONTINUOUS, "En piston (semi-continu)"),
            (BATCH_SILOS, "En silos (batch)"),
        ],
        null=True,
        blank=True,
    )

    # Rendement de l'installation de production de biométhane %
    production_efficiency = models.FloatField(null=True, blank=True)

    # Équipements installés (débitmètres et compteurs)
    BIOGAS_PRODUCTION_FLOWMETER = "BIOGAS_PRODUCTION_FLOWMETER"
    PURIFICATION_FLOWMETER = "PURIFICATION_FLOWMETER"
    FLARING_FLOWMETER = "FLARING_FLOWMETER"
    HEATING_FLOWMETER = "HEATING_FLOWMETER"
    PURIFICATION_ELECTRICAL_METER = "PURIFICATION_ELECTRICAL_METER"
    GLOBAL_ELECTRICAL_METER = "GLOBAL_ELECTRICAL_METER"

    INSTALLED_METERS_CHOICES = [
        (BIOGAS_PRODUCTION_FLOWMETER, "Débitmètre dédié à la production de biogaz"),
        (PURIFICATION_FLOWMETER, "Débitmètre dédié au volume de biogaz traité en épuration"),
        (FLARING_FLOWMETER, "Débitmètre dédié au volume de biogaz torché"),
        (HEATING_FLOWMETER, "Débitmètre dédié au volume de biogaz ou biométhane utilisé pour le chauffage du digesteur"),
        (
            PURIFICATION_ELECTRICAL_METER,
            "Compteur dédié à la consommation électrique au système d'épuration et traitement des évents",
        ),
        (GLOBAL_ELECTRICAL_METER, "Compteur dédié à la consommation électrique de l'ensemble de l'unité de production"),
    ]

    installed_meters = models.JSONField(default=list, blank=True)

    # Présence d'un hygiénisateur ?
    has_hygienization_unit = models.BooleanField(default=False)

    # Existence d'un procédé de valorisation du CO2 ?
    has_co2_valorization_process = models.BooleanField(default=False)

    # Séparation de phase du digestat ?
    has_digestate_phase_separation = models.BooleanField(default=False)

    # Étapes complémentaires de traitement du digestat brut
    raw_digestate_treatment_steps = models.CharField(max_length=128, null=True, blank=True)

    # Étape(s) complémentaire(s) de traitement de la phase liquide
    liquid_phase_treatment_steps = models.CharField(max_length=128, null=True, blank=True)

    # Étape(s) complémentaire(s) de traitement de la phase solide
    solid_phase_treatment_steps = models.CharField(max_length=128, null=True, blank=True)

    # Mode de valorisation du digestat
    SPREADING = "SPREADING"
    COMPOSTING = "COMPOSTING"
    INCINERATION_LANDFILLING = "INCINERATION_LANDFILLING"

    DIGESTATE_VALORIZATION_METHODS_CHOICES = [
        (SPREADING, "Épandage"),
        (COMPOSTING, "Compostage"),
        (INCINERATION_LANDFILLING, "Incinération / Enfouissement"),
    ]

    digestate_valorization_methods = models.JSONField(default=list, blank=True)

    # Gestion de l'épandage
    DIRECT_SPREADING = "DIRECT_SPREADING"
    SPREADING_VIA_PROVIDER = "SPREADING_VIA_PROVIDER"
    TRANSFER = "TRANSFER"
    SALE = "SALE"

    SPREADING_MANAGEMENT_METHODS_CHOICES = [
        (DIRECT_SPREADING, "Épandage direct"),
        (SPREADING_VIA_PROVIDER, "Épandage via un prestataire"),
        (TRANSFER, "Cession"),
        (SALE, "Vente"),
    ]

    spreading_management_methods = models.JSONField(default=list, blank=True)

    # En cas de vente du digestat
    DIG_AGRI_SPECIFICATIONS = "DIG_AGRI_SPECIFICATIONS"
    HOMOLOGATION = "HOMOLOGATION"
    STANDARDIZED_PRODUCT = "STANDARDIZED_PRODUCT"

    digestate_sale_type = models.CharField(
        max_length=32,
        choices=[
            (DIG_AGRI_SPECIFICATIONS, "Cahier de charges DIG Agri"),
            (HOMOLOGATION, "Homologation"),
            (STANDARDIZED_PRODUCT, "Produit normé"),
        ],
        null=True,
        blank=True,
    )
