from django.utils import timezone
from rest_framework import serializers

from core.models import CarbureLot
from tiruert.filters import OperationFilterForBalance
from tiruert.models import MacFossilFuel, Objective, Operation
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
        OperationService.check_volumes(entity_id, selected_lots, data, unit)
        OperationService.check_objectives(request, selected_lots, data, entity_id)

    @staticmethod
    def check_volumes(entity_id, selected_lots, data, unit):
        """
        Check if the selected lots exist and have enough volume to perform the operation
        """
        np_volumes, _, np_lot_ids, _, _ = TeneurService.prepare_data(entity_id, data, unit)

        available_volumes = dict(zip(map(int, np_lot_ids), map(float, np_volumes)))
        requested_volumes = {lot["id"]: lot["volume"] for lot in selected_lots}

        for lot_id, volume in requested_volumes.items():
            if lot_id not in available_volumes:
                raise serializers.ValidationError({f"lot_id: {lot_id}": OperationServiceErrors.LOT_NOT_FOUND})

            if available_volumes[lot_id] < volume:
                raise serializers.ValidationError({f"lot_id: {lot_id}": OperationServiceErrors.INSUFFICIENT_INPUT_VOLUME})

    @staticmethod
    def check_objectives(request, selected_lots, data, entity_id):
        """
        Check if the TENEUR operation respects the capped objective for the customs category
        """
        if data["type"] == Operation.TENEUR:
            year = timezone.now().year
            capped_objectives = ObjectiveService.get_capped_objectives(year)
            objective = capped_objectives.filter(customs_category=data["customs_category"]).first()
            if not objective:
                pass

            # 1. Calculate "assiette" used for objectives calculations
            macs = MacFossilFuel.objects.filter(operator_id=entity_id, year=year)
            objectives = Objective.objects.filter(year=year)
            energy_basis = ObjectiveService.calculate_energy_basis(macs, objectives)

            # 2. Calculate the balance for requested biofuel and customs category
            request.GET = request.GET.copy()
            request.GET["customs_category"] = data["customs_category"]
            request.GET["biofuel"] = data["biofuel"].code
            operations = OperationFilterForBalance(request.GET, queryset=Operation.objects.all(), request=request).qs
            balance = BalanceService.calculate_balance(operations, entity_id, None, "mj")
            balance = BalanceService.calculate_balance(operations, entity_id, None, "mj", balance, update_balance=True)
            balance = list(balance.values())[0]  # keep the first (and only) element

            # 3. Calculate the target objective for the customs category
            target = ObjectiveService.calculate_target_for_objective(objective, energy_basis)  # MJ

            # 4. Check if the objective is respected
            teneur_to_add = 0
            # Need to convert volumes from liter to MJ
            for lot in selected_lots:
                pci = CarbureLot.objects.get(id=lot["id"]).biofuel.pci_litre
                teneur_to_add += lot["volume"] * pci

            futur_teneur = balance["pending_teneur"] + balance["declared_teneur"] + teneur_to_add  # all in MJ

            if futur_teneur > target:
                raise serializers.ValidationError(
                    {f"futur_teneur: {futur_teneur} - target : {target}": OperationServiceErrors.TARGET_EXCEEDED}
                )
