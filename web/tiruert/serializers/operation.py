from django.db import transaction
from rest_framework import serializers

from tiruert.filters import OperationFilter
from tiruert.models import Operation, OperationDetail
from tiruert.serializers.operation_detail import OperationDetailSerializer
from tiruert.services.teneur import TeneurService


class OperationOutputSerializer(serializers.ModelSerializer):
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
            "from_depot",
            "to_depot",
            "created_at",
            "validity_date",
            "total",
            "details",
        ]

    details = OperationDetailSerializer(many=True, required=False)
    sector = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    biofuel = serializers.CharField(source="biofuel.code", read_only=True)
    credited_entity = serializers.CharField(source="credited_entity.name", read_only=True)
    debited_entity = serializers.CharField(source="debited_entity.name", read_only=True)
    total = serializers.SerializerMethodField()

    def get_type(self, instance):
        entity_id = self.context.get("entity_id")
        if instance.credited_entity and instance.credited_entity.id == int(entity_id) and instance.type == Operation.CESSION:
            return Operation.ACQUISITION
        else:
            return instance.type

    def get_sector(self, instance):
        return instance.sector

    def get_total(self, instance):
        total_volume = sum(detail.volume for detail in instance.details.all())
        total_saved_ghg = sum(detail.saved_ghg for detail in instance.details.all())
        return {"volume": total_volume, "saved_ghg": total_saved_ghg}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not self.context.get("details"):
            representation.pop("details", None)
        return representation


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
            "from_depot",
            "to_depot",
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
    biofuel = serializers.CharField(source="biofuel.code", read_only=True)

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
            operations = OperationFilter(request.GET, queryset=Operation.objects.all()).qs

            selected_lots, lot_ids, emissions, volumes = TeneurService.prepare_data_and_optimize(
                operations, entity_id, validated_data
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
