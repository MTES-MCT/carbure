from rest_framework import serializers

from tiruert.services.teneur import TeneurService


class OperationServiceErrors:
    INSUFFICIENT_INPUT_VOLUME = "INSUFFICIENT_INPUT_VOLUME"
    LOT_NOT_FOUND = "LOT_NOT_FOUND"


class OperationService:
    @staticmethod
    def check_volumes_before_create(entity_id, selected_lots, data):
        np_volumes, _, np_lot_ids, _, _ = TeneurService.prepare_data(entity_id, data)

        available_volumes = dict(zip(map(int, np_lot_ids), map(float, np_volumes)))
        requested_volumes = {lot["id"]: lot["volume"] for lot in selected_lots}

        for lot_id, volume in requested_volumes.items():
            if lot_id not in available_volumes:
                raise serializers.ValidationError({f"lot_id: {lot_id}": OperationServiceErrors.LOT_NOT_FOUND})

            if available_volumes[lot_id] < volume:
                raise serializers.ValidationError({f"lot_id: {lot_id}": OperationServiceErrors.INSUFFICIENT_INPUT_VOLUME})
