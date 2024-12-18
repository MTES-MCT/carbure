from django.db import models, transaction

from core.models import CarbureLot, MatierePremiere
from tiruert.models.operation_detail import OperationDetail


class Operation(models.Model):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    OPERATION_STATUSES = (
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
    )

    INCORPORATION = "INCORPORATION"
    CESSION = "CESSION"
    TENEUR = "TENEUR"
    LIVRAISON_DIRECTE = "LIVRAISON_DIRECTE"
    MAC_BIO = "MAC_BIO"
    OPERATION_TYPES = (
        (INCORPORATION, INCORPORATION),
        (CESSION, CESSION),
        (TENEUR, TENEUR),
        (LIVRAISON_DIRECTE, LIVRAISON_DIRECTE),
        (MAC_BIO, MAC_BIO),
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
    depot = models.ForeignKey("transactions.Depot", null=True, on_delete=models.SET_NULL, related_name="operations")
    created_at = models.DateTimeField(auto_now_add=True)
    validity_date = models.DateField(null=False, blank=False)

    @property
    def sector(self):
        if self.biofuel.compatible_essence:
            return "ESSENCE"
        elif self.biofuel.compatible_diesel:
            return "DIESEL"
        elif self.biofuel.code in models.Operation.SAF_BIOFUEL_TYPES:
            return "SAF"

    class Meta:
        db_table = "tiruert_operations"
        verbose_name = "Opération"
        verbose_name_plural = "Opérations"

    def is_credit(self, entity):
        if self.credited_entity is None:
            return False
        return self.credited_entity.id == int(entity)


@transaction.atomic
def create_tiruert_operations_from_lots(lots):
    # Keep only lots compatible with TIRUERT
    DELIVERY_TYPES_ACCEPTED = [CarbureLot.RFC, CarbureLot.BLENDING, CarbureLot.DIRECT]
    validated_lots = lots.filter(lot_status__in=["ACCEPTED", "FROZEN"], delivery_type__in=DELIVERY_TYPES_ACCEPTED)

    if not validated_lots:
        return []

    # Group validated_lots by delivery_type, feedstock and biofuel
    lots_by_delivery_type = {}
    for lot in validated_lots:
        key = (lot.delivery_type, lot.feedstock.category, lot.biofuel.code)
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
            status=Operation.PENDING,
            customs_category=key[1],
            biofuel=lots[0].biofuel,
            credited_entity=lots[0].carbure_client,
            debited_entity=None,
            depot=lots[0].carbure_delivery_site,
            validity_date=lots[0].delivery_date,
        )

        lots_bulk = []

        for lot in lots:
            lots_bulk.append(
                {
                    "operation": operation,
                    "lot": lot,
                    "energy": lot.volume,
                    "saved_ghg": calculate_saved_CO2_emissions(lot),
                }
            )

        OperationDetail.objects.bulk_create([OperationDetail(**data) for data in lots_bulk])


def calculate_saved_CO2_emissions(lot):
    saved_co2 = (lot.ghg_reference * lot.pci * lot.volume - lot.lvh_amount * lot.ghg_total) / 1000000
    return saved_co2
