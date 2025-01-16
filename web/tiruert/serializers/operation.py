from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from tiruert.models import Operation, OperationDetail
from tiruert.serializers.operation_detail import OperationDetailSerializer
from tiruert.services.teneur import TeneurService


class DepotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class EntitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


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

    from_depot = DepotSerializer()
    to_depot = DepotSerializer()
    credited_entity = EntitySerializer()
    debited_entity = EntitySerializer()
    details = OperationDetailSerializer(many=True, required=False)
    sector = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    biofuel = serializers.CharField(source="biofuel.code", read_only=True)
    volume = serializers.SerializerMethodField()
    # emission_rate_per_mj = serializers.SerializerMethodField()

    def get_type(self, instance):
        entity_id = self.context.get("entity_id")
        if instance.is_acquisition(entity_id):
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
    class Meta:
        model = Operation
        fields = [
            "type",
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

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context.get("request")
            entity_id = request.query_params.get("entity_id")

            try:
                selected_lots, lot_ids, emissions, fun = TeneurService.prepare_data_and_optimize(
                    entity_id,
                    validated_data,
                )

            except ValueError as error:
                raise ValidationError(str(error))

            if validated_data["type"] in [
                Operation.INCORPORATION,
                Operation.MAC_BIO,
                Operation.LIVRAISON_DIRECTE,
                Operation.TENEUR,
                Operation.DEVALUATION,
            ]:
                validated_data["status"] = Operation.ACCEPTED
            else:
                validated_data["status"] = Operation.PENDING

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
