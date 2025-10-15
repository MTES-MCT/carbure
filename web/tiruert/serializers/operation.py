from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from core.models import Pays
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
    sector = serializers.CharField(source="_sector", read_only=True)
    type = serializers.CharField(source="_type", read_only=True)
    biofuel = serializers.CharField(source="biofuel.code", read_only=True)
    quantity = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    renewable_energy_share = serializers.FloatField()
    _entity = serializers.CharField(read_only=True)
    _depot = serializers.CharField(read_only=True)

    def get_volume_l(self, instance) -> float:
        if getattr(instance, "_volume", None) is not None:
            return instance._volume

        return instance.volume

    def get_quantity(self, instance) -> float:
        if getattr(instance, "_quantity", None) is not None:
            return round(instance._quantity, 2)

        volume = self.get_volume_l(instance)
        return round(instance.volume_to_quantity(volume, self.context.get("unit")), 2)

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
            "renewable_energy_share",
            "credited_entity",
            "debited_entity",
            "_entity",
            "from_depot",
            "to_depot",
            "_depot",
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
            "renewable_energy_share",
            "credited_entity",
            "debited_entity",
            "_entity",
            "from_depot",
            "to_depot",
            "_depot",
            "export_country",
            "created_at",
            "validation_date",
            "durability_period",
            "quantity",
            "quantity_mj",
            "avoided_emissions",
            "unit",
            "details",
        ]

    avoided_emissions = serializers.SerializerMethodField()
    quantity_mj = serializers.SerializerMethodField()

    def get_avoided_emissions(self, instance) -> float:
        return round(sum(detail.avoided_emissions for detail in instance.details.all()), 2)

    def get_quantity_mj(self, instance) -> float:
        volume = self.get_volume_l(instance)
        return round(instance.volume_to_quantity(volume, "mj"), 2)


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
            "status",
        ]
        extra_kwargs = {
            "biofuel": {"required": True},
            "customs_category": {"required": True},
            "debited_entity": {"required": True},
        }

    export_country = serializers.SlugRelatedField(
        slug_field="code_pays", queryset=Pays.objects.all(), required=False, allow_null=True
    )
    lots = OperationLotSerializer(many=True, required=True)

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context.get("request")
            entity_id = request.entity.id
            unit = request.unit
            selected_lots = validated_data.pop("lots")

            OperationService.perform_checks_before_create(request, entity_id, selected_lots, validated_data, unit)

            if validated_data["type"] in [Operation.TRANSFERT]:
                if validated_data.get("status") is not Operation.DRAFT:
                    validated_data["status"] = Operation.PENDING
            elif validated_data["type"] in [
                Operation.INCORPORATION,
                Operation.MAC_BIO,
                Operation.LIVRAISON_DIRECTE,
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
        fields = ["to_depot", "status"]


class OperationCorrectionSerializer(serializers.Serializer):
    correction_volume = serializers.FloatField()

    def update(self, operation, validated_data):
        with transaction.atomic():
            correction_volume = validated_data["correction_volume"]
            debit = correction_volume < 0
            credit = not debit

            # New operation which carry the new lots with the correction volume
            correction = Operation.objects.create(
                type=Operation.CUSTOMS_CORRECTION,
                status=Operation.VALIDATED,
                customs_category=operation.customs_category,
                biofuel=operation.biofuel,
                from_depot=operation.to_depot if debit else None,
                to_depot=operation.to_depot if credit else None,
                debited_entity=operation.credited_entity if debit else None,
                credited_entity=operation.credited_entity if credit else None,
                validation_date=datetime.now(),
            )

            # If the correction volume is positive, we add volume to the first lot id of the operation
            if correction_volume > 0:
                first_lot = operation.details.first()
                OperationDetail.objects.create(
                    operation=correction,
                    lot_id=first_lot.lot_id,
                    volume=abs(correction_volume),
                    emission_rate_per_mj=first_lot.emission_rate_per_mj,  # gCO2/MJ
                )
            # If the correction volume is negative
            # We first need to check if the correction volume is greater than the operation volume
            # Then we empty each lot of the operation until the correction volume is reached
            else:
                if operation.volume < abs(correction_volume):
                    raise serializers.ValidationError({"error": "NOT_ENOUGH_VOLUME"})

                for lot in operation.details.all():
                    if correction_volume == 0:
                        break
                    if lot.volume < abs(correction_volume):
                        correction_volume += lot.volume
                        new_lot_volume = lot.volume
                    else:
                        new_lot_volume = abs(correction_volume)
                        correction_volume = 0

                    OperationDetail.objects.create(
                        operation=correction,
                        lot_id=lot.lot_id,
                        volume=new_lot_volume,
                        emission_rate_per_mj=lot.emission_rate_per_mj,  # gCO2/MJ
                    )
        return correction
