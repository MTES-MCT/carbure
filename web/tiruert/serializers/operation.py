import numpy as np
from django.db import transaction
from rest_framework import serializers

from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.filters import OperationFilter
from tiruert.models import Operation, OperationDetail
from tiruert.serializers.operation_detail import OperationDetailSerializer
from tiruert.services.balance import BalanceService


class OperationOutputSerializer(serializers.ModelSerializer):
    details = OperationDetailSerializer(many=True, required=False)

    class Meta:
        model = Operation
        fields = [
            "id",
            "type",
            "status",
            "sector",
            "customs_category",
            "biofuel",
            "credited_entity",
            "debited_entity",
            "depot",
            "created_at",
            "validity_date",
            "details",
        ]

    sector = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_type(self, instance):
        entity_id = self.context.get("entity_id")
        if instance.credited_entity and instance.credited_entity.id == int(entity_id) and instance.type == Operation.CESSION:
            return Operation.ACQUISITION
        else:
            return instance.type

    def get_sector(self, instance):
        if instance.biofuel.compatible_essence:
            return "ESSENCE"
        elif instance.biofuel.compatible_diesel:
            return "DIESEL"
        elif instance.biofuel.code in SAF_BIOFUEL_TYPES:
            return "SAF"


class OperationInputSerializer(serializers.ModelSerializer):
    NO_SUITABLE_LOTS_FOUND = "NO_SUITABLE_LOTS_FOUND"

    class Meta:
        model = Operation
        fields = [
            "type",
            "status",
            "customs_category",
            "biofuel",
            "credited_entity",
            "debited_entity",
            "depot",
            "validity_date",
            "target_volume",
            "target_emission",
        ]
        extra_kwargs = {
            "biofuel": {"required": True},
            "customs_category": {"required": True},
            "debited_entity": {"required": True},
            "target_volume": {"required": True},
            "target_emission": {"required": True},
        }

    target_volume = serializers.FloatField()
    target_emission = serializers.FloatField()
    status = serializers.SerializerMethodField()

    def get_status(self, instance):
        if instance["type"] in [
            Operation.INCORPORATION,
            Operation.MAC_BIO,
            Operation.LIVRAISON_DIRECTE,
            Operation.TENEUR,
            Operation.DEVALUATION,
        ]:
            return Operation.ACCEPTED

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context.get("request")
            entity_id = request.query_params.get("entity_id")
            by_lot = True
            operations = OperationFilter(request.GET, queryset=Operation.objects.all()).qs

            # Calculate balance of debited entity
            balance = BalanceService.calculate_balance(operations, entity_id, by_lot)

            # Rearrange balance in an array of all volumes sums and an array of all ghg sums
            # For each we have something like:
            # array([30.52876597, 42.1162736 , 30.07384206, 25.05628985, 85.52717505])
            volumes, emissions, lot_ids = np.array([]), np.array([]), np.array([])

            for key, value in balance.items():
                customs_cat, biofuel, lot_id = key
                volumes = np.append(volumes, value["volume"]["credit"] - value["volume"]["debit"])
                emissions = np.append(emissions, value["ghg"]["credit"] - value["ghg"]["debit"])
                lot_ids = np.append(lot_ids, lot_id)

            # print(volumes)
            # print(emissions)
            # print(lot_ids)

            selected_lots = BalanceService.optimize_biofuel_blending(
                volumes,
                emissions,
                validated_data.pop("target_volume"),
                validated_data.pop("target_emission"),
            )

            if not selected_lots:
                raise serializers.ValidationError(self.NO_SUITABLE_LOTS_FOUND)

            # Create the operation
            operation = Operation.objects.create(**validated_data)

            # Create the details
            detail_operations_data = []
            for idx, lot_volume in selected_lots.items():
                detail_operations_data.append(
                    {
                        "operation": operation,
                        "lot_id": lot_ids[idx],
                        "volume": lot_volume,
                        "saved_ghg": emissions[idx] * lot_volume / volumes[idx],
                    }
                )

            OperationDetail.objects.bulk_create(
                [OperationDetail(**data) for data in detail_operations_data],
            )

            return operation
