from django.db import models

from core.models import MatierePremiere, Pays
from core.utils import truncate
from tiruert.services.energy import energy_mj


class OperationQuerySet(models.QuerySet):
    def exclude_informative(self):
        """Drop operations that only carry information and must not impact any computation."""
        return self.exclude(type__in=Operation.BALANCE_EXCLUDED_TYPES)


class OperationManager(models.Manager.from_queryset(OperationQuerySet)):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("biofuel", "credited_entity", "debited_entity", "from_depot", "to_depot")
            .only(
                # Champs de l'opération
                "id",
                "type",
                "status",
                "customs_category",
                "validation_date",
                "created_at",
                "renewable_energy_share",
                "export_recipient",
                "objective_sector",
                "durability_period",
                "declaration_year",
                # Relations nécessaires
                "biofuel_id",
                "credited_entity_id",
                "debited_entity_id",
                "from_depot_id",
                "to_depot_id",
                "export_country_id",
                # Champs des modèles liés utilisés
                "biofuel__code",
                "biofuel__pci_litre",
                "biofuel__compatible_essence",
                "biofuel__compatible_diesel",
                "biofuel__compatible_gpl",
                "biofuel__masse_volumique",
                "biofuel__renewable_energy_share",
                "credited_entity__name",
                "debited_entity__name",
                "from_depot__name",
                "to_depot__name",
            )
        )


class Operation(models.Model):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"  # Acquisition
    REJECTED = "REJECTED"  # Acquisition
    CANCELED = "CANCELED"
    DECLARED = "DECLARED"  # Teneur validation
    CORRECTED = "CORRECTED"  # By customs
    VALIDATED = "VALIDATED"  # By customs
    DRAFT = "DRAFT"  # For transfert operations
    AUTO = "AUTO"

    OPERATION_STATUSES = (
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
        (CANCELED, CANCELED),
        (DECLARED, DECLARED),
        (CORRECTED, CORRECTED),
        (VALIDATED, VALIDATED),
        (DRAFT, DRAFT),
        (AUTO, AUTO),
    )

    INCORPORATION = "INCORPORATION"
    CESSION = "CESSION"
    TENEUR = "TENEUR"
    LIVRAISON_DIRECTE = "LIVRAISON_DIRECTE"
    MAC_BIO = "MAC_BIO"
    ACQUISITION = "ACQUISITION"  # Only for display purposes
    EXPORTATION = "EXPORTATION"
    DEVALUATION = "DEVALUATION"
    CUSTOMS_CORRECTION = "CUSTOMS_CORRECTION"
    TRANSFERT = "TRANSFERT"
    EXPEDITION = "EXPEDITION"
    EXPIRATION = "EXPIRATION"
    REPORT = "REPORT"  # Used once for switching from TIRUERT to IRICC regulation
    YEARLY_BALANCE = "YEARLY_BALANCE"  # Snapshot of the balance at the closing of a declaration year
    OPERATION_TYPES = (
        (INCORPORATION, INCORPORATION),
        (CESSION, CESSION),
        (TENEUR, TENEUR),
        (LIVRAISON_DIRECTE, LIVRAISON_DIRECTE),
        (MAC_BIO, MAC_BIO),
        (EXPORTATION, EXPORTATION),
        (EXPEDITION, EXPEDITION),
        (DEVALUATION, DEVALUATION),
        (CUSTOMS_CORRECTION, CUSTOMS_CORRECTION),
        (TRANSFERT, TRANSFERT),
        (EXPIRATION, EXPIRATION),
        (REPORT, REPORT),
        (YEARLY_BALANCE, YEARLY_BALANCE),
    )

    API_CREATABLE_TYPES = [TRANSFERT, EXPORTATION, EXPEDITION, TENEUR, DEVALUATION]
    API_DELETABLE_TYPES = [TRANSFERT, EXPORTATION, EXPEDITION, TENEUR, DEVALUATION, CESSION]

    # Types that generate initial credit volumes (from physical operations)
    CREDIT_TYPES = [INCORPORATION, MAC_BIO, LIVRAISON_DIRECTE]

    # Informative types: they are listed in the API but must never impact any volume computation
    BALANCE_EXCLUDED_TYPES = [YEARLY_BALANCE]

    # Statuses considered active in balance calculation (credits + debits)
    ACTIVE_STATUSES = [PENDING, ACCEPTED, VALIDATED, DECLARED, DRAFT]

    # Definitive statuses for confirmed operations (no longer pending)
    CONFIRMED_STATUSES = [ACCEPTED, VALIDATED, DECLARED]

    ESSENCE = "ESSENCE"
    GAZOLE = "GAZOLE"
    CARBUREACTEUR = "CARBURÉACTEUR"
    GPL = "GPL"
    MARITIME = "MARITIME"
    SECTOR_CODE_CHOICES = (
        (ESSENCE, ESSENCE),
        (GAZOLE, GAZOLE),
        (CARBUREACTEUR, CARBUREACTEUR),
        (GPL, GPL),
        (MARITIME, MARITIME),
    )

    type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    status = models.CharField(max_length=12, choices=OPERATION_STATUSES, default=PENDING)
    customs_category = models.CharField(max_length=20, choices=MatierePremiere.MP_CATEGORIES, default=MatierePremiere.CONV)
    biofuel = models.ForeignKey("core.Biocarburant", null=True, blank=False, on_delete=models.SET_NULL)
    credited_entity = models.ForeignKey(
        "core.Entity", null=True, on_delete=models.deletion.CASCADE, related_name="from_operations"
    )
    debited_entity = models.ForeignKey(
        "core.Entity", null=True, on_delete=models.deletion.CASCADE, related_name="to_operations"
    )
    from_depot = models.ForeignKey(
        "transactions.Depot", null=True, on_delete=models.SET_NULL, related_name="operations_from_depot"
    )
    to_depot = models.ForeignKey(
        "transactions.Depot", null=True, on_delete=models.SET_NULL, related_name="operations_to_depot"
    )
    # Specific field for exportation/expedition
    export_country = models.ForeignKey(
        Pays, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="operations_country"
    )
    # Specific field for exportation/expedition
    export_recipient = models.CharField(max_length=255, blank=True)
    # Specific field for Teneur operations
    declaration_year = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    validation_date = models.DateField(null=True, blank=True)
    renewable_energy_share = models.FloatField(default=1)
    durability_period = models.CharField(max_length=6, blank=True, null=True)

    # Allows overriding the sector objective, when the declared sector differs from the natural sector of the biofuel
    objective_sector = models.CharField(max_length=20, choices=SECTOR_CODE_CHOICES, null=True, blank=True)

    LOSS = "LOSS"
    DOWNGRADING = "DOWNGRADING"
    OTHER = "OTHER"
    DEVALUATION_TYPES = (
        (LOSS, "Perte"),
        (DOWNGRADING, "Déclassement"),
        (OTHER, "Autre"),
    )
    devaluation_type = models.CharField(max_length=20, choices=DEVALUATION_TYPES, null=True, blank=True)

    objects = OperationManager()

    @property
    def sector(self):
        from tiruert.services.operation import OperationService

        return OperationService.define_sector(self.biofuel)

    @property
    def volume_unsigned(self):
        return sum([detail.volume for detail in self.details.all()])

    @property
    def volume(self):
        """Returns the volume in liters, rounded to 2 decimal places."""
        if getattr(self, "_volume", None) is not None:
            return truncate(self._volume)

        return truncate(self.volume_unsigned)  # unsigned

    @property
    def energy(self):
        """Returns the energy in MJ, rounded to 0 decimal places."""
        if getattr(self, "_energy", None) is not None:
            return truncate(self._energy, 0)

        return truncate(
            energy_mj(self.volume_unsigned, self.biofuel.pci_litre, self.renewable_energy_share),
            0,
        )  # unsigned

    @property
    def avoided_emissions(self):
        """Returns the avoided emissions in tCO2, rounded to 2 decimal places."""
        if getattr(self, "_avoided_emissions", None) is not None:
            return truncate(self._avoided_emissions)

        return truncate(sum(detail.avoided_emissions for detail in self.details.all()))  # in tCO2

    class Meta:
        db_table = "tiruert_operations"
        verbose_name = "Opération"
        verbose_name_plural = "Opérations"

    def is_credit(self, entity_id):
        if self.credited_entity is None:
            return False
        return self.credited_entity.id == int(entity_id)

    def is_acquisition(self, entity_id):
        if self.credited_entity is None:
            return False
        return self.credited_entity.id == int(entity_id) and self.type == Operation.CESSION
