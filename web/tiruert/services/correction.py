from collections import defaultdict
from copy import copy

from django.db import transaction
from django.db.models import Q

from core.models import CarbureLot
from core.utils import truncate
from tiruert.models import Operation, OperationDetail
from tiruert.services.balance import BalanceService
from tiruert.services.operation import OperationService


class CorrectionService:
    @staticmethod
    @transaction.atomic
    def create_correction_operations_for_lot_volume_update(lot_ids: list[int]):
        """
        Align the TIRUERT volume of each lot with its current CarbureLot volume.

        For each (lot, customs_category, biofuel) credited by an initial operation, the gap between
        the expected volume and the net volume already credited (initial operation + previous
        corrections) is turned into a CORRECTION operation:
        - volume added: credit, whatever the lot balance is
        - volume removed: debit, only when the lot balance of the credited entity covers it
        """
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
                # Insufficient balance: debt repayment is not handled yet
                if available < abs(volume_delta):
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
        - volume: the net volume credited (initial operation + corrections)
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
