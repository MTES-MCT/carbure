from collections import defaultdict
from decimal import ROUND_CEILING, Decimal
from math import isfinite

from django.db.models import Q, Sum
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.models import Biocarburant, CarbureLot, Entity
from core.utils import truncate
from tiruert.models import OperationDetail, TiruertDebt
from tiruert.services.energy import (
    GHG_REFERENCE_RED_II,
    avoided_emissions_tco2,
    energy_mj,
)
from tiruert.services.teneur import TeneurService

# Volumes and TCO2 debts carry 2 decimals: anything below is float residue of `value - repaid`
MIN_OPEN_VOLUME = 0.005
MIN_OPEN_TCO2 = 0.005


class DebtService:
    @staticmethod
    def get_open_debts(entity_id, biofuel_id=None, customs_category=None, debt_type: str | None = TiruertDebt.VOLUME):
        """Open debts, oldest first; select one type (VOLUME by default) or both with None."""
        debts = TiruertDebt.objects.with_remaining().filter(
            Q(type=TiruertDebt.VOLUME, remaining__gte=MIN_OPEN_VOLUME)
            | Q(type=TiruertDebt.TCO2, remaining__gte=MIN_OPEN_TCO2),
            entity_id=entity_id,
        )
        if debt_type is not None:
            debts = debts.filter(type=debt_type)
        if biofuel_id is not None:
            debts = debts.filter(biofuel_id=biofuel_id)
        if customs_category is not None:
            debts = debts.filter(customs_category=customs_category)
        return debts.order_by("created_at", "id")

    @staticmethod
    def summarize_open_debts(entity_id) -> list[dict]:
        """
        Remaining debt volume (L) and emissions (tCO2) per (biofuel, customs_category).

        Returns [{"biofuel": Biocarburant, "customs_category", "remaining_volume", "remaining_tco2"}].
        """
        rows = list(
            DebtService.get_open_debts(entity_id, debt_type=None)
            .order_by()
            .values("biofuel_id", "customs_category")
            .annotate(
                remaining_volume=Sum("remaining", filter=Q(type=TiruertDebt.VOLUME), default=0.0),
                remaining_tco2=Sum("remaining", filter=Q(type=TiruertDebt.TCO2), default=0.0),
            )
            .order_by("biofuel_id", "customs_category")
        )
        biofuels = Biocarburant.objects.in_bulk({row["biofuel_id"] for row in rows})

        return [
            {
                "biofuel": biofuels[row["biofuel_id"]],
                "customs_category": row["customs_category"],
                "remaining_volume": truncate(row["remaining_volume"]),
                "remaining_tco2": truncate(max(0.0, row["remaining_tco2"])),
            }
            for row in rows
        ]

    @staticmethod
    def lock_entities(entity_ids):
        """Lock the specified entities in ID order to serialize debt operations."""
        list(Entity.objects.select_for_update().filter(id__in=entity_ids).order_by("id").values_list("id", flat=True))

    @staticmethod
    def lock_debts(entity, biofuel, customs_category, debt_type):
        """Lock debts matching the repayment scope."""
        list(
            TiruertDebt.objects.select_for_update()
            .filter(entity=entity, biofuel=biofuel, customs_category=customs_category, type=debt_type)
            .values_list("id", flat=True)
        )

    @staticmethod
    def _tco2_per_liter(pci_litre, renewable_share, emission_rate):
        """Return the avoided emissions, in tCO2, attributable to one liter."""
        return avoided_emissions_tco2(
            energy_mj(Decimal(1), Decimal(str(pci_litre)), Decimal(str(renewable_share))),
            Decimal(str(emission_rate)),
            Decimal(str(GHG_REFERENCE_RED_II)),
        )

    @staticmethod
    def _tco2_stock(data):
        """Build available lots dict as (volume, tCO2 per liter), best contribution first."""
        volumes, _emissions, lot_ids, _enforced, _target = TeneurService.prepare_data(data)
        lot_queryset = CarbureLot.objects.select_related("biofuel")

        if data.get("ges_bound_min") is not None:
            lot_queryset = lot_queryset.filter(ghg_reduction_red_ii__gte=data["ges_bound_min"])
        if data.get("ges_bound_max") is not None:
            lot_queryset = lot_queryset.filter(ghg_reduction_red_ii__lte=data["ges_bound_max"])

        lots = lot_queryset.in_bulk(int(lot_id) for lot_id in lot_ids)

        rates = OperationDetail.objects.get_effective_emission_rates_by_lot(lots)
        stock = {}
        for lot_id, available in zip(lot_ids, volumes):
            lot_id = int(lot_id)
            rate = rates.get(lot_id)
            if rate is None or lot_id not in lots:
                continue
            contribution = DebtService._tco2_per_liter(
                lots[lot_id].biofuel.pci_litre,
                data["biofuel"].renewable_energy_share,
                rate,
            )
            volume = Decimal(str(truncate(float(available))))
            if volume > 0 and contribution > 0:
                stock[lot_id] = (volume, contribution)
        return dict(sorted(stock.items(), key=lambda item: (-item[1][1], item[0])))

    @staticmethod
    def _allocate_tco2(debts, stock):
        """Allocate available stock to debts based on tCO2 contribution."""
        available_volumes = {lot_id: volume for lot_id, (volume, _rate) in stock.items()}
        plans = []
        applied_by_debt = {}
        for debt in debts:
            remaining = Decimal(str(debt.remaining))
            lots = {}
            for lot_id, (_volume, rate) in stock.items():
                if remaining <= 0:
                    break
                volume_needed = (remaining / rate).quantize(Decimal("0.01"), rounding=ROUND_CEILING)  # transform tCO2 to L
                taken = min(available_volumes[lot_id], volume_needed)
                if taken <= 0:
                    continue
                lots[lot_id] = float(taken)
                contribution = taken * rate
                applied_by_debt[debt.id] = applied_by_debt.get(debt.id, Decimal(0)) + contribution
                remaining -= contribution
                available_volumes[lot_id] -= taken
            if lots:
                plans.append((debt, lots))
        return plans, applied_by_debt, available_volumes

    @staticmethod
    def _tco2_repayment_totals(debts, added_contributions):
        """Return the debt reduction and remaining balance at 0.01 tCO2 precision."""
        repaid_total = Decimal(0)
        remaining_total = Decimal(0)
        for debt in debts:
            debt_remaining = Decimal(str(debt.remaining))
            added = added_contributions.get(debt.id, Decimal(0))
            repaid = min(debt_remaining, added)
            repaid_total += repaid
            remaining_total += debt_remaining - repaid
        return repaid_total, remaining_total

    @staticmethod
    def _tco2_debt_total(debts):
        return sum((Decimal(str(truncate(debt.remaining))) for debt in debts), Decimal(0))

    @staticmethod
    def simulate_tco2_repayment(data):
        """Preview repayment of open tCO2 debts using the available lots."""
        debts = list(
            DebtService.get_open_debts(
                data["debited_entity"].id, data["biofuel"].id, data["customs_category"], TiruertDebt.TCO2
            )
        )
        if not debts:
            raise serializers.ValidationError({"debt": "NO_OPEN_TCO2_DEBT"})

        stock = DebtService._tco2_stock(data)
        if not stock:
            raise serializers.ValidationError({"lots": "NO_AVAILABLE_STOCK"})

        plans, applied_by_debt, _ = DebtService._allocate_tco2(debts, stock)

        repaid_tco2, remaining_tco2 = DebtService._tco2_repayment_totals(debts, applied_by_debt)
        if repaid_tco2 <= 0:
            raise serializers.ValidationError({"lots": "NO_TCO2_REPAYMENT_AT_PRECISION"})

        selected = defaultdict(Decimal)
        for _debt, lots in plans:
            for lot_id, volume in lots.items():
                selected[lot_id] += Decimal(str(volume))

        debt_tco2 = DebtService._tco2_debt_total(debts)
        return {
            "selected_lots": [{"lot_id": lot_id, "volume": float(volume)} for lot_id, volume in selected.items()],
            "total_volume": float(sum(selected.values())),
            "repaid_tco2": float(repaid_tco2),
            "remaining_tco2": float(remaining_tco2),
            "debt_tco2": float(debt_tco2),
        }

    @staticmethod
    def plan_tco2_repayment(data, lots):
        """Lock debts and spread submitted lot volumes FIFO over open tCO2 debts."""
        entity = data["debited_entity"]
        DebtService.lock_entities([entity.id])
        DebtService.lock_debts(entity, data["biofuel"], data["customs_category"], TiruertDebt.TCO2)

        debts = list(DebtService.get_open_debts(entity.id, data["biofuel"].id, data["customs_category"], TiruertDebt.TCO2))
        if not debts:
            raise serializers.ValidationError(
                {"debt": [_("Aucune dette à acquitter pour ce biocarburant et cette catégorie.")]}
            )

        if any(
            not isfinite(lot["volume"]) or float(Decimal(str(lot["volume"])).quantize(Decimal("0.01"))) != lot["volume"]
            for lot in lots
        ):
            raise serializers.ValidationError({"volume": "INVALID_CENTILITER_VOLUME"})

        requested = DebtService._merge_lots(lots)
        rates = OperationDetail.objects.get_effective_emission_rates_by_lot(requested.keys())
        selected_stock = {}
        for lot_id, volume in requested.items():
            rate = rates.get(lot_id)
            if rate is None:
                raise serializers.ValidationError({f"lot_id: {lot_id}": "LOT_EMISSION_RATE_NOT_FOUND"})

            contribution = DebtService._tco2_per_liter(
                data["biofuel"].pci_litre,
                data["biofuel"].renewable_energy_share,
                rate,
            )
            if contribution <= 0:
                raise serializers.ValidationError({"lots": "NO_TCO2_REPAYMENT_AT_PRECISION"})
            selected_stock[lot_id] = (Decimal(str(volume)), contribution)

        plans, applied_by_debt, unallocated = DebtService._allocate_tco2(debts, selected_stock)
        if any(vol_left > 0 for vol_left in unallocated.values()):
            raise serializers.ValidationError({"volume": [_("Le volume à acquitter dépasse la dette restante.")]})

        repaid_tco2, _remaining_tco2 = DebtService._tco2_repayment_totals(debts, applied_by_debt)
        if repaid_tco2 <= 0:
            raise serializers.ValidationError({"lots": "NO_TCO2_REPAYMENT_AT_PRECISION"})
        return plans

    @staticmethod
    def plan_volume_repayment(entity, biofuel, customs_category, lots) -> list[tuple[TiruertDebt, dict[int, float]]]:
        """
        Spread the requested lots over the open debts of (entity, biofuel, customs_category), oldest debt first.

        - lots: list of {"id", "volume"} (L) picked among the entity lots of the same biofuel and category.
        Returns [(debt, {lot_id: volume})], one entry per repaid debt: a lot can be split between two debts.
        Must run inside a transaction: the debts are locked first so that two concurrent repayments cannot
        spend the same remaining volume.
        """
        DebtService.lock_debts(entity, biofuel, customs_category, TiruertDebt.VOLUME)

        requested = DebtService._merge_lots(lots)

        debts = list(DebtService.get_open_debts(entity.id, biofuel.id, customs_category).select_related("lot"))
        if not debts:
            raise serializers.ValidationError(
                {"debt": [_("Aucune dette à acquitter pour ce biocarburant et cette catégorie.")]}
            )

        remaining_by_debt = {debt.id: truncate(debt.remaining) for debt in debts}
        total_requested = truncate(sum(requested.values()))
        total_remaining = truncate(sum(remaining_by_debt.values()))
        if total_requested > total_remaining:
            raise serializers.ValidationError(
                {
                    "volume": [
                        _("Le volume à acquitter ({requested} L) dépasse la dette restante ({remaining} L).").format(
                            requested=total_requested, remaining=total_remaining
                        )
                    ]
                }
            )

        debts_by_id = {debt.id: debt for debt in debts}
        split = DebtService._split_lots_between_debts(requested, remaining_by_debt)
        return [(debts_by_id[debt_id], lot_volumes) for debt_id, lot_volumes in split.items()]

    @staticmethod
    def _split_lots_between_debts(lots: dict[int, float], debts: dict[int, float]) -> dict[int, dict[int, float]]:
        """
        Fill each debt in order with the volume of the lots in order, a lot can be split between two debts.

        - lots: {lot_id: volume (L) to use}
        - debts: {debt_id: volume (L) to repay}, oldest debt first
        Returns {debt_id: {lot_id: volume}}, without the debts that receive nothing.
        """
        lot_left = dict(lots)
        split = {}
        for debt_id, debt_left in debts.items():
            for lot_id in lot_left:
                taken = truncate(min(lot_left[lot_id], debt_left))
                if taken > 0:
                    split.setdefault(debt_id, {})[lot_id] = taken  # {debt_id: {lot_id: taken}}
                    lot_left[lot_id] = truncate(lot_left[lot_id] - taken)  # remaining volume of the lot
                    debt_left = truncate(debt_left - taken)
        return split

    @staticmethod
    def _merge_lots(lots) -> dict[int, float]:
        """Requested volume (L) per lot id, in request order. Rejects non-positive volumes."""
        requested = defaultdict(float)
        for lot in lots:
            volume = truncate(lot["volume"])
            if volume <= 0:
                raise serializers.ValidationError({"volume": [_("Le volume à acquitter doit être supérieur à zéro.")]})
            requested[lot["id"]] = truncate(requested[lot["id"]] + volume)
        return requested
