from copy import copy
from decimal import Decimal

from django.db import models, transaction

from core.models import CarbureLot, MatierePremiere, Pays
from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.models.operation_detail import OperationDetail


class OperationManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("biofuel", "credited_entity", "debited_entity", "from_depot", "to_depot")
            .prefetch_related("details")
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
    OPERATION_STATUSES = (
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
        (CANCELED, CANCELED),
        (DECLARED, DECLARED),
        (CORRECTED, CORRECTED),
        (VALIDATED, VALIDATED),
        (DRAFT, DRAFT),
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
    )

    ESSENCE = "ESSENCE"
    GAZOLE = "GAZOLE"
    CARBUREACTEUR = "CARBURÉACTEUR"
    SECTOR_CODE_CHOICES = (
        (ESSENCE, ESSENCE),
        (GAZOLE, GAZOLE),
        (CARBUREACTEUR, CARBUREACTEUR),
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
    created_at = models.DateTimeField(auto_now_add=True)
    validation_date = models.DateField(null=True, blank=True)
    renewable_energy_share = models.FloatField(default=1)
    durability_period = models.CharField(max_length=6, blank=True, null=True)

    objects = OperationManager()

    @property
    def sector(self):
        if self.biofuel.compatible_essence:
            return Operation.ESSENCE
        elif self.biofuel.compatible_diesel:
            return Operation.GAZOLE
        elif self.biofuel.code in SAF_BIOFUEL_TYPES:
            return Operation.CARBUREACTEUR

    @property
    def volume(self):
        return sum([detail.volume for detail in self.details.all()])

    @property
    def volume_l(self):
        if getattr(self, "_volume", None) is not None:
            return self._volume

        return self.volume

    @property
    def avoided_emissions(self):
        return round(sum(detail.avoided_emissions for detail in self.details.all()), 2)  # in tCO2

    class Meta:
        db_table = "tiruert_operations"
        verbose_name = "Opération"
        verbose_name_plural = "Opérations"

    def is_credit(self, entity):
        if self.credited_entity is None:
            return False
        return self.credited_entity.id == int(entity)

    def is_acquisition(self, entity_id):
        if self.credited_entity is None:
            return False
        return self.credited_entity.id == int(entity_id) and self.type == Operation.CESSION

    def quantity(self, unit="l"):
        if getattr(self, "_quantity", None) is not None:
            return round(self._quantity, 2)

        volume = self.volume_l
        return round(self.volume_to_quantity(volume, unit), 2)

    def volume_to_quantity(self, volume, unit):
        if unit == "mj":
            return volume * self.biofuel.pci_litre
        elif unit == "kg":
            return volume * self.biofuel.masse_volumique
        else:
            return volume


@transaction.atomic
def create_tiruert_operations_from_lots(lots):
    valid_lots = keep_valid_lots(lots)
    valid_lots = remove_existing_lots(valid_lots)

    if not valid_lots:
        return []

    valid_lots = list(valid_lots)
    valid_lots = ep2_processing(valid_lots)

    # Group validated_lots by delivery_type, feedstock, biofuel and depot
    lots_by_delivery_type = {}
    for lot in valid_lots:
        key = (lot.delivery_type, lot.feedstock.category, lot.biofuel.code, lot.carbure_delivery_site)
        if key not in lots_by_delivery_type:
            lots_by_delivery_type[key] = []
        lots_by_delivery_type[key].append(lot)

    matching_types = {
        CarbureLot.RFC: Operation.MAC_BIO,
        CarbureLot.BLENDING: Operation.INCORPORATION,
        CarbureLot.DIRECT: Operation.LIVRAISON_DIRECTE,
    }

    for key, lots in lots_by_delivery_type.items():
        operation = Operation.objects.create(
            type=matching_types[key[0]],
            status=Operation.VALIDATED,  # TODO: Set to PENDING when DGGDI validation will be implemented
            customs_category=key[1],
            biofuel=lots[0].biofuel,
            credited_entity=lots[0].carbure_client,
            debited_entity=None,
            from_depot=None,
            to_depot=lots[0].carbure_delivery_site,
            renewable_energy_share=lots[0].biofuel.renewable_energy_share,
            durability_period=lots[0].period,
        )

        lots_bulk = []

        for lot in lots:
            lots_bulk.append(
                {
                    "operation": operation,
                    "lot": lot,
                    "volume": round(lot.volume, 2),  # litres
                    "emission_rate_per_mj": lot.ghg_total,  # gCO2/MJ (input algo d'optimisation)
                }
            )

        OperationDetail.objects.bulk_create([OperationDetail(**data) for data in lots_bulk])


def keep_valid_lots(lots):
    # Keep only lots compatible with TIRUERT
    DELIVERY_TYPES_ACCEPTED = [CarbureLot.RFC, CarbureLot.BLENDING, CarbureLot.DIRECT]
    return lots.filter(lot_status__in=["ACCEPTED", "FROZEN"], delivery_type__in=DELIVERY_TYPES_ACCEPTED)


def remove_existing_lots(lots):
    # Remove lots that already have an operation to avoid duplicates
    existing_lots = OperationDetail.objects.filter(lot__in=lots).values_list("lot_id").distinct()
    return lots.exclude(id__in=existing_lots)


def ep2_processing(lots):
    # We split the EP2 lots into two new lots (but we don't save them yet in the database)
    # 40% of the volume will be converted to CONV and 60% will be EP2AM
    result_lots = []

    for lot in lots:
        if lot.feedstock.code == "EP2":
            new_lot_conv = copy(lot)
            new_lot_conv.feedstock = copy(lot.feedstock)
            new_lot_conv.feedstock.category = MatierePremiere.CONV
            volume_decimal = Decimal(str(lot.volume))
            new_lot_conv.volume = round(float(volume_decimal * Decimal("0.4")), 2)

            new_lot_ep2 = copy(lot)
            new_lot_ep2.feedstock = copy(lot.feedstock)
            new_lot_ep2.feedstock.category = MatierePremiere.EP2AM
            new_lot_ep2.volume = round(float(volume_decimal * Decimal("0.6")), 2)

            result_lots.append(new_lot_conv)
            result_lots.append(new_lot_ep2)
        else:
            result_lots.append(lot)

    return result_lots
