from django.db import transaction
from rest_framework import serializers

from tiruert.models import Operation, OperationDetail
from tiruert.serializers.operation_detail import OperationDetailSerializer
from tiruert.services.operation import OperationService


class OperationDepotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class OperationEntitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class BaseOperationSerializer(serializers.ModelSerializer):
    from_depot = OperationDepotSerializer()
    to_depot = OperationDepotSerializer()
    credited_entity = OperationEntitySerializer()
    debited_entity = OperationEntitySerializer()
    details = OperationDetailSerializer(many=True, required=False)
    sector = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    biofuel = serializers.CharField(source="biofuel.code", read_only=True)
    quantity = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()

    def get_type(self, instance) -> str:
        entity_id = self.context.get("entity_id")
        if instance.is_acquisition(entity_id):
            return Operation.ACQUISITION
        else:
            return instance.type

    def get_sector(self, instance) -> str:
        return instance.sector

    def get_volume_l(self, instance) -> float:
        return sum(detail.volume for detail in instance.details.all())

    def get_quantity(self, instance) -> float:
        volume = self.get_volume_l(instance)
        return instance.volume_to_quantity(volume, self.context.get("unit"))

    def get_unit(self, instance) -> str:
        return self.context.get("unit")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not self.context.get("details"):
            representation.pop("details", None)
        return representation


class OperationListSerializer(BaseOperationSerializer):
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
            "export_country",
            "created_at",
            "quantity",
            "unit",
            "details",
        ]


class OperationSerializer(BaseOperationSerializer):
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
            "export_country",
            "created_at",
            "validation_date",
            "quantity",
            "avoided_emissions",
            "unit",
            "details",
        ]

    avoided_emissions = serializers.SerializerMethodField()

    def get_avoided_emissions(self, instance) -> float:
        return sum(detail.avoided_emissions for detail in instance.details.all())


class OperationLotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    volume = serializers.FloatField()
    emission_rate_per_mj = serializers.FloatField()


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
            "export_country",
            "lots",
        ]
        extra_kwargs = {
            "biofuel": {"required": True},
            "customs_category": {"required": True},
            "debited_entity": {"required": True},
            "lots": {"required": True},
        }

    lots = OperationLotSerializer(many=True)

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context.get("request")
            entity_id = request.query_params.get("entity_id")
            selected_lots = validated_data.pop("lots")

            OperationService.check_volumes_before_create(entity_id, selected_lots, validated_data)

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
            for lot in selected_lots:
                detail_operations_data.append(
                    {
                        "operation": operation,
                        "lot_id": lot["id"],
                        "volume": lot["volume"],
                        "emission_rate_per_mj": lot["emission_rate_per_mj"],  # gCO2/MJ
                    }
                )

            OperationDetail.objects.bulk_create(
                [OperationDetail(**data) for data in detail_operations_data],
            )

            return operation


class OperationUpdateSerializer(serializers.ModelSerializer):
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
            "export_country",
        ]
