from rest_framework import serializers

from core.models import CarbureLot
from tiruert.filters import OperationFilterForBalance
from tiruert.models import Operation
from tiruert.services.balance import BalanceService
from tiruert.services.objective import ObjectiveService
from tiruert.services.teneur import TeneurService


class OperationServiceErrors:
    INSUFFICIENT_INPUT_VOLUME = "INSUFFICIENT_INPUT_VOLUME"
    LOT_NOT_FOUND = "LOT_NOT_FOUND"
    TARGET_EXCEEDED = "TARGET_EXCEEDED"


class OperationService:
    @staticmethod
    def perform_checks_before_create(request, entity_id, selected_lots, data, unit):
        OperationService.check_volumes(selected_lots, data, unit)
        OperationService.check_objectives_compliance(request, selected_lots, data, entity_id)

    @staticmethod
    def check_volumes(selected_lots, data, unit):
        """
        Check if the selected lots exist and have enough volume to perform the operation
        """
        np_volumes, _, np_lot_ids, _, _ = TeneurService.prepare_data(data, unit)

        available_volumes = dict(zip(map(int, np_lot_ids), map(float, np_volumes)))
        requested_volumes = {lot["id"]: lot["volume"] for lot in selected_lots}

        for lot_id, volume in requested_volumes.items():
            if lot_id not in available_volumes:
                raise serializers.ValidationError({f"lot_id: {lot_id}": OperationServiceErrors.LOT_NOT_FOUND})

            if available_volumes[lot_id] < volume:
                raise serializers.ValidationError({f"lot_id: {lot_id}": OperationServiceErrors.INSUFFICIENT_INPUT_VOLUME})

    @staticmethod
    def check_objectives_compliance(request, selected_lots, data, entity_id):
        """
        Check if the TENEUR operation respects the capped objective for the customs category
        """
        if data["type"] == Operation.TENEUR:
            # 1. Get the target for the customs category
            target = ObjectiveService.calculate_target_for_specific_category(data["customs_category"], request.entity.id)

            # Case for reach objective and no objective, no need to do this check compliance
            if target is None:
                return

            # 2. Calculate the balance for requested biofuel and customs category
            request.GET = request.GET.copy()
            request.GET["customs_category"] = data["customs_category"]
            request.GET["biofuel"] = data["biofuel"].code
            operations = OperationFilterForBalance(request.GET, queryset=Operation.objects.all(), request=request).qs
            balance = BalanceService.calculate_balance(operations, entity_id, None, "mj")
            balance = list(balance.values())[0]  # keep the first (and only one) element

            # 3. Convert the teneur to add from liters to MJ
            teneur_to_add = 0
            for lot in selected_lots:
                pci = CarbureLot.objects.get(id=lot["id"]).biofuel.pci_litre
                teneur_to_add += lot["volume"] * pci

            # 4. Check if the futur teneur is below the target
            futur_teneur = balance["pending_teneur"] + balance["declared_teneur"] + teneur_to_add  # all in MJ

            if futur_teneur > target:
                raise serializers.ValidationError(
                    {f"futur_teneur: {futur_teneur} - target : {target}": OperationServiceErrors.TARGET_EXCEEDED}
                )
