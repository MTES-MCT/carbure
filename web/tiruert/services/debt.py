from collections import defaultdict

from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.models import Biocarburant
from core.utils import truncate
from tiruert.models import TiruertDebt

# Volumes carry 2 decimals: anything below is float residue of `value - repaid`
MIN_OPEN_VOLUME = 0.005


class DebtService:
    @staticmethod
    def get_open_debts(entity_id, biofuel_id=None, customs_category=None):
        """
        Open VOLUME debts of an entity (remaining volume > 0), oldest first.
        """
        debts = TiruertDebt.objects.with_remaining().filter(
            entity_id=entity_id,
            type=TiruertDebt.VOLUME,
            remaining__gte=MIN_OPEN_VOLUME,
        )
        if biofuel_id is not None:
            debts = debts.filter(biofuel_id=biofuel_id)
        if customs_category is not None:
            debts = debts.filter(customs_category=customs_category)
        return debts.order_by("created_at", "id")

    @staticmethod
    def summarize_open_debts(entity_id) -> list[dict]:
        """
        Remaining debt volume (L) per (biofuel, customs_category) for an entity.

        Returns [{"biofuel": Biocarburant, "customs_category", "remaining_volume"}].
        """
        rows = list(
            DebtService.get_open_debts(entity_id)
            .order_by()
            .values("biofuel_id", "customs_category")
            .annotate(remaining_volume=Sum("remaining"))
            .order_by("biofuel_id", "customs_category")
        )
        biofuels = Biocarburant.objects.in_bulk({row["biofuel_id"] for row in rows})

        return [
            {
                "biofuel": biofuels[row["biofuel_id"]],
                "customs_category": row["customs_category"],
                "remaining_volume": truncate(row["remaining_volume"]),
            }
            for row in rows
        ]

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

    @staticmethod
    def plan_repayment(entity, biofuel, customs_category, lots) -> list[tuple[TiruertDebt, dict[int, float]]]:
        """
        Spread the requested lots over the open debts of (entity, biofuel, customs_category), oldest debt first.

        - lots: list of {"id", "volume"} (L) picked among the entity lots of the same biofuel and category.
        Returns [(debt, {lot_id: volume})], one entry per repaid debt: a lot can be split between two debts.
        Must run inside a transaction: the debts are locked first so that two concurrent repayments cannot
        spend the same remaining volume.
        """
        list(
            TiruertDebt.objects.select_for_update()
            .filter(entity=entity, biofuel=biofuel, customs_category=customs_category, type=TiruertDebt.VOLUME)
            .values_list("id", flat=True)
        )

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
