from collections import defaultdict
from copy import copy
from decimal import ROUND_DOWN, Decimal

from django.db import transaction
from django.db.models import Q, QuerySet, Sum
from rest_framework.exceptions import ValidationError

from core.models import CarbureLot
from core.utils import truncate
from tiruert.models import Operation, OperationDetail, TiruertDebt
from tiruert.services.balance import BalanceService
from tiruert.services.debt import DebtService
from tiruert.services.energy import energy_mj
from tiruert.services.operation import OperationService


class CorrectionService:
    @staticmethod
    def get_corrected_operation_ids(operation: Operation, accessible_operations: QuerySet[Operation]) -> list[int]:
        """Return visible operations associated with a GHG correction."""
        ghg_delta = operation.ghg_delta
        if operation.type != Operation.CORRECTION or ghg_delta is None:
            return []

        candidates = Q(corrected=True) & (
            Q(type__in=Operation.CREDIT_TYPES)
            | Q(type=Operation.CORRECTION, details__volume__gt=0)
            | Q(type=Operation.TENEUR)
        )
        if ghg_delta < 0:
            candidates |= Q(type=Operation.TRANSFERT) & (Q(corrected=True) | Q(status=Operation.ACCEPTED))

        detail = next(iter(operation.details.all()))
        return list(
            accessible_operations.filter(
                candidates,
                details__lot_id=detail.lot_id,
                customs_category=operation.customs_category,
                biofuel_id=operation.biofuel_id,
                created_at__lt=operation.created_at,
            )
            .order_by("pk")
            .values_list("pk", flat=True)
            .distinct()
        )

    @staticmethod
    @transaction.atomic
    def create_correction_operations_for_lot_update(lot_ids: list[int]):
        """Apply GHG and volume corrections for the given lots in one transaction."""
        CorrectionService.create_correction_operations_for_lot_ghg_update(lot_ids)
        CorrectionService.create_correction_operations_for_lot_volume_update(lot_ids)

    @staticmethod
    @transaction.atomic
    def create_correction_operations_for_lot_ghg_update(lot_ids: list[int]):
        """Correct confirmed credits and affected debits after lot emission-rate changes."""
        lot_ids = OperationService.lock_lots_for_update(lot_ids)
        if not lot_ids:
            return

        details = (
            OperationDetail.objects.filter(lot_id__in=lot_ids)
            .filter(
                Q(
                    operation__type__in=Operation.CREDIT_TYPES,
                    operation__status__in=Operation.CONFIRMED_STATUSES,
                )
                | Q(
                    operation__type=Operation.CORRECTION,
                    operation__status__in=Operation.CONFIRMED_STATUSES,
                    volume__gt=0,
                )
                | Q(
                    operation__type=Operation.TENEUR,
                    operation__status__in=[Operation.PENDING, Operation.DECLARED, Operation.CORRECTED],
                )
                | Q(
                    operation__type=Operation.TRANSFERT,
                    operation__status__in=[Operation.DRAFT, Operation.PENDING, Operation.ACCEPTED, Operation.CORRECTED],
                )
            )
            .select_related(None)
            .select_related("operation", "lot")
            .select_for_update()
            .only(
                "id",
                "lot_id",
                "operation_id",
                "emission_rate_per_mj",
                "emission_rate_per_mj_delta",
                "lot__ghg_total",
                "operation__type",
                "operation__status",
                "operation__credited_entity_id",
                "operation__customs_category",
                "operation__biofuel_id",
                "operation__renewable_energy_share",
                "operation__durability_period",
                "operation__declaration_year",
            )
            .order_by("operation__created_at", "id")
        )
        details_by_lot_category_biofuel = defaultdict(list)
        for detail in details:
            key = (detail.lot_id, detail.operation.customs_category, detail.operation.biofuel_id)
            details_by_lot_category_biofuel[key].append(detail)

        debtor_ids = (
            Operation.objects.filter(
                type=Operation.TRANSFERT,
                status__in=[Operation.ACCEPTED, Operation.CORRECTED],
                details__lot_id__in=lot_ids,
                debited_entity__isnull=False,
            )
            .values_list("debited_entity_id", flat=True)
            .distinct()
        )
        DebtService.lock_entities(debtor_ids)

        updated_details = []
        corrected_operation_ids = set()
        for grouped_details in details_by_lot_category_biofuel.values():
            corrected_details = CorrectionService._apply_ghg_correction(grouped_details)
            updated_details.extend(corrected_details)
            corrected_operation_ids.update(detail.operation_id for detail in corrected_details)

        OperationDetail.objects.bulk_update(updated_details, ["emission_rate_per_mj_delta"])
        Operation.objects.filter(id__in=corrected_operation_ids).update(corrected=True)
        Operation.objects.filter(id__in=corrected_operation_ids).exclude(
            Q(type=Operation.TENEUR, status=Operation.PENDING)
            | Q(type=Operation.TRANSFERT, status__in=[Operation.DRAFT, Operation.PENDING])
        ).update(status=Operation.CORRECTED)

    @staticmethod
    def _apply_ghg_correction(grouped_details: list[OperationDetail]) -> list[OperationDetail]:
        """
        Apply the lot's emission-rate change to details sharing a lot, category and biofuel.

        Create the corresponding correction and, depending on the direction of the change,
        a transfer debt or corrections for transfer recipients. Return the modified details
        for bulk update; confirmed transfers are excluded when the emission rate increases.
        """
        initial = next((detail for detail in grouped_details if detail.operation.type in Operation.CREDIT_TYPES), None)
        if initial is None:
            return []

        previous_rate = Decimal(str(initial.effective_emission_rate_per_mj))
        current_rate = Decimal(str(initial.lot.ghg_total))
        delta = current_rate - previous_rate
        if delta == 0:
            return []

        source = initial.operation
        if delta > 0:
            CorrectionService._create_transfer_tco2_debt(initial, delta)
        CorrectionService._create_ghg_correction(initial, previous_rate, delta, source.credited_entity_id)
        if delta < 0:
            CorrectionService._copy_ghg_correction_to_transfer_recipients(initial, previous_rate, delta)

        corrected_details = [
            detail
            for detail in grouped_details
            if delta < 0
            or detail.operation.type != Operation.TRANSFERT
            or detail.operation.status in [Operation.DRAFT, Operation.PENDING]
        ]
        for detail in corrected_details:
            detail.emission_rate_per_mj_delta = float(current_rate - Decimal(str(detail.emission_rate_per_mj)))
        return corrected_details

    @staticmethod
    def _create_transfer_tco2_debt(initial: OperationDetail, delta: Decimal) -> None:
        """Create a TCO2 debt for the initiator of confirmed transfers if the emissions loss is significant."""
        source = initial.operation
        transfers = CorrectionService._confirmed_transfer_details(
            [initial.lot_id], source.customs_category, source.biofuel_id
        )
        initiator_id = transfers.values_list("operation__debited_entity_id", flat=True).first()
        if initiator_id is None:
            return
        transfers = transfers.filter(operation__debited_entity_id=initiator_id)
        loss = sum(
            (
                energy_mj(
                    Decimal(str(detail.volume)),
                    Decimal(str(detail.lot.biofuel.pci_litre)),
                    Decimal(str(detail.operation.renewable_energy_share)),
                )
                * delta
                / Decimal(1_000_000)
                for detail in transfers
            ),
            Decimal(0),
        )
        if loss >= Decimal("0.01"):
            TiruertDebt.objects.create(
                type=TiruertDebt.TCO2,
                value=float(loss.quantize(Decimal("0.01"), rounding=ROUND_DOWN)),
                entity_id=initiator_id,
                biofuel_id=source.biofuel_id,
                customs_category=source.customs_category,
                lot_id=initial.lot_id,
            )

    @staticmethod
    def _confirmed_transfer_details(lot_ids, customs_category, biofuel_id):
        """Return accepted or corrected transfer details in chronological order."""
        return OperationDetail.objects.filter(
            lot_id__in=lot_ids,
            operation__type=Operation.TRANSFERT,
            operation__customs_category=customs_category,
            operation__biofuel_id=biofuel_id,
            operation__status__in=[Operation.ACCEPTED, Operation.CORRECTED],
        ).order_by("operation__created_at", "id")

    @staticmethod
    def _copy_ghg_correction_to_transfer_recipients(
        initial: OperationDetail, previous_rate: Decimal, delta: Decimal
    ) -> None:
        """Create a GHG correction for each distinct transfer recipient other than the initial creditor."""
        source = initial.operation
        recipients = (
            Operation.objects.filter(
                Q(status=Operation.ACCEPTED) | Q(status=Operation.CORRECTED, corrected=True),
                type=Operation.TRANSFERT,
                details__lot_id=initial.lot_id,
                customs_category=source.customs_category,
                biofuel_id=source.biofuel_id,
            )
            .order_by()
            .values_list("credited_entity_id", flat=True)
            .distinct()
        )
        for recipient_id in recipients:
            if recipient_id is None:
                raise ValidationError({"credited_entity": "TRANSFER_RECIPIENT_REQUIRED"})
            if recipient_id != source.credited_entity_id:
                CorrectionService._create_ghg_correction(initial, previous_rate, delta, recipient_id)

    @staticmethod
    def _create_ghg_correction(
        initial: OperationDetail, previous_rate: Decimal, delta: Decimal, credited_entity_id: int | None
    ) -> Operation:
        """Create a zero-volume GHG correction based on the initial credit operation."""
        source = initial.operation
        return OperationService.create_operation_with_details(
            {
                "type": Operation.CORRECTION,
                "status": Operation.VALIDATED,
                "customs_category": source.customs_category,
                "biofuel_id": source.biofuel_id,
                "credited_entity_id": credited_entity_id,
                "renewable_energy_share": source.renewable_energy_share,
                "durability_period": source.durability_period,
                "declaration_year": source.declaration_year,
            },
            [
                {
                    "lot_id": initial.lot_id,
                    "volume": 0,
                    "emission_rate_per_mj": float(previous_rate),
                    "emission_rate_per_mj_delta": float(delta),
                }
            ],
        )

    @staticmethod
    @transaction.atomic
    def create_correction_operations_for_lot_volume_update(lot_ids: list[int]):
        """
        Align the TIRUERT volume of each lot with its current CarbureLot volume.

        For each (lot, customs_category, biofuel) credited by an initial operation, the gap between
        the expected volume and the net volume already credited (initial operation + previous
        corrections) is turned into a CORRECTION operation:
        - volume added: credit it whatever the lot balance is, existing debts are left untouched
        - volume removed: debit when the lot balance of the credited entity covers it, otherwise record a
          TiruertDebt of the whole volume (no debit)
        """
        if not lot_ids:
            return

        lot_ids = OperationService.lock_lots_for_update(lot_ids)
        if not lot_ids:
            return

        credit_data_by_lot_category_biofuel = CorrectionService._get_current_credited_volume_by_lot_category_biofuel(lot_ids)
        corrected_lots = CarbureLot.objects.filter(id__in=lot_ids).select_related("feedstock", "biofuel")
        # Convert a copy so the in-memory conversions (ETH 15°, EP2 split, EMAG) never leak into the lot objects themselves
        lots = OperationService.convert_lots_for_operations([copy(lot) for lot in corrected_lots])

        for lot in lots:
            credit_data = credit_data_by_lot_category_biofuel.get(
                (
                    lot.id,
                    lot.feedstock.category,
                    lot.biofuel_id,
                )
            )
            if credit_data is None:
                continue

            volume_delta = truncate(lot.volume - credit_data["volume"])
            if volume_delta == 0:
                continue

            entity_id = credit_data["entity_id"]
            if volume_delta < 0:
                available = CorrectionService._get_lot_balance(
                    lot.id,
                    entity_id,
                    lot.feedstock.category,
                    lot.biofuel,
                )
                if available < abs(volume_delta):
                    TiruertDebt.objects.create(
                        type=TiruertDebt.VOLUME,
                        value=abs(volume_delta),
                        entity_id=entity_id,
                        biofuel=lot.biofuel,
                        customs_category=lot.feedstock.category,
                        lot_id=lot.id,
                    )
                    continue

            CorrectionService._create_volume_correction(lot, credit_data, volume_delta)

    @staticmethod
    def _get_current_credited_volume_by_lot_category_biofuel(lot_ids: list[int]) -> dict[tuple, dict]:
        """
        Net volume credited per (lot_id, customs_category, biofuel_id), with the entity credited by the
        initial operation. Lots without an initial credit operation are absent from the result.

        Returns {key: {"entity_id", "durability_period", "volume"}}:
        - entity_id: the entity credited by the initial operation
        - durability_period: the durability period of the initial operation
        - volume: the net volume credited (initial operation + corrections) minus the VOLUME debts of the lot,
          so that a debt is not recreated by the next correction
        """
        rows = (
            OperationDetail.objects.filter(lot_id__in=lot_ids, operation__status__in=Operation.ACTIVE_STATUSES)
            .filter(Q(operation__type__in=Operation.CREDIT_TYPES) | Q(operation__type=Operation.CORRECTION))
            .order_by("operation_id")
            .values_list(
                "lot_id",
                "volume",
                "operation__type",
                "operation__customs_category",
                "operation__biofuel_id",
                "operation__credited_entity_id",
                "operation__durability_period",
            )
        )

        credit_volume_by_lot_category_biofuel = defaultdict(
            lambda: {"entity_id": None, "durability_period": None, "volume": 0.0}
        )
        for lot_id, volume, operation_type, customs_category, biofuel_id, credited_entity_id, durability_period in rows:
            credit_data = credit_volume_by_lot_category_biofuel[(lot_id, customs_category, biofuel_id)]
            if operation_type == Operation.CORRECTION:
                credit_data["volume"] += volume if credited_entity_id else -volume
            else:
                credit_data["entity_id"] = credited_entity_id
                credit_data["durability_period"] = durability_period
                credit_data["volume"] += volume

        debts = (
            TiruertDebt.objects.filter(lot_id__in=lot_ids, type=TiruertDebt.VOLUME)
            .values("lot_id", "customs_category", "biofuel_id")
            .annotate(total=Sum("value"))
        )
        for debt in debts:
            key = (debt["lot_id"], debt["customs_category"], debt["biofuel_id"])
            if key in credit_volume_by_lot_category_biofuel:
                credit_volume_by_lot_category_biofuel[key]["volume"] -= debt["total"]

        return {
            key: credit_data
            for key, credit_data in credit_volume_by_lot_category_biofuel.items()
            if credit_data["entity_id"] is not None
        }

    @staticmethod
    def _get_lot_balance(lot_id: int, entity_id: int, customs_category: str, biofuel) -> float:
        """Available volume (L) of one lot for one entity."""
        operations = (
            Operation.objects.filter(biofuel=biofuel, customs_category=customs_category)
            .filter(Q(credited_entity_id=entity_id) | Q(debited_entity_id=entity_id))
            .distinct()
        )
        balance = BalanceService.calculate_balance(
            operations,
            entity_id,
            BalanceService.GROUP_BY_LOT,
            "l",
            detail_filters={"lot_ids": [lot_id]},
        )
        return sum(entry["available_balance"] for entry in balance.values())

    @staticmethod
    def _create_volume_correction(converted_lot, credit_data: dict, volume_delta: float):
        """Create a validated credit or debit correction for the converted lot's volume change."""
        is_credit = volume_delta > 0
        entity_id = credit_data["entity_id"]

        operation_data = {
            "type": Operation.CORRECTION,
            "status": Operation.VALIDATED,
            "customs_category": converted_lot.feedstock.category,
            "biofuel": converted_lot.biofuel,
            "credited_entity_id": entity_id if is_credit else None,
            "debited_entity_id": None if is_credit else entity_id,
            "from_depot": None,
            "to_depot": None,
            "renewable_energy_share": converted_lot.biofuel.renewable_energy_share,
            "durability_period": credit_data["durability_period"],
        }
        details_data = [
            {
                "lot_id": converted_lot.id,
                "volume": abs(volume_delta),
                "emission_rate_per_mj": converted_lot.ghg_total,
            }
        ]

        return OperationService.create_operation_with_details(operation_data, details_data)
