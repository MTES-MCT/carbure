from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
            "volume",
            # "emission_rate_per_mj",
            "details",
        ]

    details = OperationDetailSerializer(many=True, required=False)
    sector = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    biofuel = serializers.CharField(source="biofuel.code", read_only=True)
    credited_entity = serializers.CharField(source="credited_entity.name", read_only=True)
    debited_entity = serializers.CharField(source="debited_entity.name", read_only=True)
    volume = serializers.SerializerMethodField()
    # emission_rate_per_mj = serializers.SerializerMethodField()

    def get_type(self, instance):
        entity_id = self.context.get("entity_id")
        if instance.credited_entity and instance.credited_entity.id == int(entity_id) and instance.type == Operation.CESSION:
            return Operation.ACQUISITION
        else:
            return instance.type

    def get_sector(self, instance):
        return instance.sector

    def get_volume(self, instance):
        return sum(detail.volume for detail in instance.details.all())

    # def get_emission_rate_per_mj(self, instance):
    #    return instance.details.first().emission_rate_per_mj

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

            selected_lots, lot_ids, emissions, fun = TeneurService.prepare_data_and_optimize(
                entity_id,
                validated_data,
            )

            if not selected_lots:
                raise ValidationError(OperationInputSerializer.NO_SUITABLE_LOTS_FOUND)

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
                        "emission_rate_per_mj": emissions[idx] + fun,
                    }
                )

            OperationDetail.objects.bulk_create(
                [OperationDetail(**data) for data in detail_operations_data],
            )

            return operation
