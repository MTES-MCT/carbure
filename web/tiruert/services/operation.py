from copy import copy
from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from core.models import CarbureLot, MatierePremiere
from tiruert.filters import OperationFilterForBalance
from tiruert.models import Operation, OperationDetail
from tiruert.services.balance import BalanceService
from tiruert.services.objective import ObjectiveService
from tiruert.services.teneur import TeneurService


class OperationServiceErrors:
    INSUFFICIENT_INPUT_VOLUME = "INSUFFICIENT_INPUT_VOLUME"
    LOT_NOT_FOUND = "LOT_NOT_FOUND"
    TARGET_EXCEEDED = "TARGET_EXCEEDED"
    ENTITY_ID_DO_NOT_MATCH_DEBITED_ID = "ENTITY_ID_DO_NOT_MATCH_DEBITED_ID"


class OperationService:
    @staticmethod
    def perform_checks_before_create(request, entity_id, selected_lots, data, unit, declaration_year):
        OperationService.check_debited_entity(entity_id, data)
        OperationService.check_volumes(selected_lots, data, unit)
        OperationService.check_objectives_compliance(request, selected_lots, data, entity_id)
        OperationService.check_declaration_year(declaration_year, data)

    @staticmethod
    def check_debited_entity(entity_id, data):
        """
        Check if the debited entity is the same as entity_id passed in the request
        """
        if data["debited_entity"].id != entity_id:
            raise serializers.ValidationError({"debited_entity": OperationServiceErrors.ENTITY_ID_DO_NOT_MATCH_DEBITED_ID})

    @staticmethod
    def check_volumes(selected_lots, data, unit):
        """
        Check if the selected lots exist and have enough volume to perform the operation
        """
        np_volumes, _, np_lot_ids, _, _ = TeneurService.prepare_data(data, unit)

        # Round available volumes to 8 decimals to match optimization algorithm precision
        available_volumes = {int(lot_id): round(float(volume), 8) for lot_id, volume in zip(np_lot_ids, np_volumes)}
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

    @staticmethod
    def check_declaration_year(declaration_year, validated_data):
        if not declaration_year:
            raise serializers.ValidationError({"declaration_year": "Declaration year is required"})

        validated_data["declaration_year"] = declaration_year

    @staticmethod
    def define_operation_status(validated_data):
        """
        Define the operation status based on the entity type and operation type
        """
        auto_accepted_types = [
            Operation.INCORPORATION,
            Operation.MAC_BIO,
            Operation.LIVRAISON_DIRECTE,
            Operation.DEVALUATION,
        ]

        if validated_data["type"] in auto_accepted_types:
            validated_data["status"] = Operation.ACCEPTED
        elif validated_data.get("status") != Operation.DRAFT:
            validated_data["status"] = Operation.PENDING

    @staticmethod
    @transaction.atomic
    def create_operations_from_lots(lots):
        """
        Create TIRUERT operations from CarbureLots.

        Groups lots by delivery_type, feedstock category, biofuel and depot,
        then creates one operation per group with associated details.
        """
        valid_lots = OperationService.filter_valid_lots(lots)
        valid_lots = OperationService.remove_existing_lots(valid_lots)

        if not valid_lots:
            return []

        valid_lots = list(valid_lots)
        valid_lots = OperationService.process_ep2_lots(valid_lots)

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

    @staticmethod
    def filter_valid_lots(lots):
        """
        Keep only lots compatible with TIRUERT.

        Valid lots must have:
        - lot_status in ["ACCEPTED", "FROZEN"]
        - delivery_type in [RFC, BLENDING, DIRECT]
        """
        DELIVERY_TYPES_ACCEPTED = [CarbureLot.RFC, CarbureLot.BLENDING, CarbureLot.DIRECT]
        return lots.filter(lot_status__in=["ACCEPTED", "FROZEN"], delivery_type__in=DELIVERY_TYPES_ACCEPTED)

    @staticmethod
    def remove_existing_lots(lots):
        """
        Remove lots that already have an operation to avoid duplicates.
        """
        existing_lots = OperationDetail.objects.filter(lot__in=lots).values_list("lot_id").distinct()
        return lots.exclude(id__in=existing_lots)

    @staticmethod
    def process_ep2_lots(lots):
        """
        Split EP2 lots into two new lots (not saved to database).

        EP2 lots are split as:
        - 40% of volume → CONV category
        - 60% of volume → EP2AM category
        """
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
