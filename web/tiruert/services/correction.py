from collections import defaultdict

from django.db import transaction

from core.utils import truncate
from tiruert.models import Operation, OperationDetail
from tiruert.services.declaration_period import DeclarationPeriodService
from tiruert.services.energy import avoided_emissions_tco2, energy_mj
from tiruert.services.teneur import GHG_REFERENCE_RED_II


class CorrectionService:
    @staticmethod
    def _get_active_details_by_lot(lot_ids: list[int]) -> dict[int, list[OperationDetail]]:
        """Return active non-informative details grouped by lot id."""
        details = (
            OperationDetail.objects.select_related("operation", "lot", "lot__biofuel")
            .exclude_informative()
            .filter(
                lot_id__in=lot_ids,
                operation__status__in=Operation.ACTIVE_STATUSES,
            )
        )

        details_by_lot: dict[int, list[OperationDetail]] = defaultdict(list)
        for detail in details:
            if detail.lot_id is None or detail.lot is None or detail.lot.biofuel is None:
                continue
            details_by_lot[detail.lot_id].append(detail)

        return details_by_lot

    @staticmethod
    def _compute_detail_delta(detail: OperationDetail, emission_rate_new: float) -> float:
        """Compute signed avoided-emissions delta for one detail line."""
        operation = detail.operation
        lot = detail.lot
        energy = energy_mj(
            detail.volume,
            lot.biofuel.pci_litre,
            getattr(operation, "renewable_energy_share", 1),
        )

        if operation.type == Operation.CORRECTION and detail.avoided_emissions_tco2 is not None:
            # Existing correction lines represent already-applied adjustments.
            old_avoided = detail.avoided_emissions_tco2
            new_avoided = 0.0
        else:
            old_avoided = avoided_emissions_tco2(
                energy,
                detail.emission_rate_per_mj,
                GHG_REFERENCE_RED_II,
            )
            new_avoided = avoided_emissions_tco2(
                energy,
                emission_rate_new,
                GHG_REFERENCE_RED_II,
            )

        return new_avoided - old_avoided

    @staticmethod
    def _compute_deltas_by_entity(
        lot_details: list[OperationDetail], emission_rate_new: float
    ) -> dict[int, dict[str, float]]:
        """Aggregate signed deltas by entity and direction (credit/debit)."""
        deltas_by_entity = defaultdict(lambda: {"credit": 0.0, "debit": 0.0})

        for detail in lot_details:
            operation = detail.operation
            delta = CorrectionService._compute_detail_delta(detail, emission_rate_new)

            if operation.credited_entity_id:
                deltas_by_entity[operation.credited_entity_id]["credit"] += delta
            if operation.debited_entity_id:
                deltas_by_entity[operation.debited_entity_id]["debit"] += delta

        return deltas_by_entity

    @staticmethod
    def _build_correction_payload(lot, lot_id: int, entity_id: int, net_delta: float) -> tuple[dict, list[dict]]:
        """Build operation and detail payloads for one correction line."""
        is_credit = net_delta >= 0
        details_data = [
            {
                "lot_id": lot_id,
                "volume": 0,
                "emission_rate_per_mj": lot.ghg_total,
                "avoided_emissions_tco2": abs(net_delta),
            }
        ]

        operation_data = {
            "type": Operation.CORRECTION,
            "status": Operation.VALIDATED,
            "customs_category": lot.feedstock.category,
            "biofuel": lot.biofuel,
            "credited_entity_id": entity_id if is_credit else None,
            "debited_entity_id": entity_id if not is_credit else None,
            "from_depot": None,
            "to_depot": None,
            "renewable_energy_share": lot.biofuel.renewable_energy_share,
            "declaration_year": DeclarationPeriodService.get_current_declaration_year(),
        }

        return operation_data, details_data

    @staticmethod
    @transaction.atomic
    def create_correction_operations_for_lot_ghg_update(lot_ids: list[int]):
        """
        Create one CORRECTION operation per impacted entity when a lot ghg_total is updated.

        For each entity, create one OperationDetail (same lot, volume=0) with a non-signed
        avoided_emissions_tco2 value. The sign is carried by operation direction:
        - credited_entity_id when net delta >= 0
        - debited_entity_id when net delta < 0

        The override field avoided_emissions_tco2 stores the delta magnitude in tCO2,
        and operation direction carries the sign for balance/objective computations.
        """
        if not lot_ids:
            return

        details_by_lot = CorrectionService._get_active_details_by_lot(lot_ids)

        for lot_id, lot_details in details_by_lot.items():
            lot = lot_details[0].lot
            deltas_by_entity = CorrectionService._compute_deltas_by_entity(lot_details, lot.ghg_total)

            for entity_id, entity_deltas in deltas_by_entity.items():
                net_delta = truncate(entity_deltas["credit"] - entity_deltas["debit"])

                if net_delta == 0:
                    continue

                operation_data, details_data = CorrectionService._build_correction_payload(
                    lot,
                    lot_id,
                    entity_id,
                    net_delta,
                )

                from tiruert.services.operation import OperationService

                OperationService.create_operation_with_details(operation_data, details_data)
