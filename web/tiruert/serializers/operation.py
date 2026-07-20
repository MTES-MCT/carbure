from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from core.models import Pays
from core.serializers import CountrySerializer
from core.utils import truncate
from tiruert.models import Operation, OperationDetail
from tiruert.serializers.balance import BalanceBiofuelSerializer
from tiruert.serializers.fields import RoundedFloatField
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
    biofuel = BalanceBiofuelSerializer(read_only=True)
    quantity = serializers.SerializerMethodField()
    _entity = serializers.CharField(read_only=True)
    _depot = serializers.CharField(read_only=True)
    avoided_emissions = serializers.SerializerMethodField()
    year = serializers.IntegerField(source="declaration_year", read_only=True)

    def get_quantity(self, instance) -> float:
        return instance.quantity()

    def get_avoided_emissions(self, instance) -> float:
        if getattr(instance, "_avoided_emissions", None) is not None:
            return round(instance._avoided_emissions, 2)
        return instance.avoided_emissions

    def get_fields(self):
        fields = super().get_fields()
        if not self.context.get("details"):
            fields.pop("details", None)
        return fields


class OperationListSerializer(BaseOperationSerializer):
    quantity = RoundedFloatField(source="_quantity", read_only=True)
    avoided_emissions = RoundedFloatField(source="_avoided_emissions", read_only=True)

    class Meta:
        model = Operation
        fields = [
            "id",
            "type",
            "status",
            "sector",
            "objective_sector",
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
            "details",
            "avoided_emissions",
            "year",
        ]


class OperationSerializer(BaseOperationSerializer):
    class Meta:
        model = Operation
        fields = [
            "id",
            "type",
            "status",
            "sector",
            "objective_sector",
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
            "export_recipient",
            "created_at",
            "validation_date",
            "durability_period",
            "quantity",
            "quantity_mj",
            "avoided_emissions",
            "unit",
            "details",
            "year",
        ]

    quantity_mj = serializers.SerializerMethodField()
    export_country = CountrySerializer(read_only=True)

    def get_quantity_mj(self, instance) -> float:
        return int(instance.quantity(unit="mj", force=True))


class OperationLotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    volume = serializers.FloatField()


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
            "export_recipient",
            "objective_sector",
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

    def validate_type(self, value):
        if value not in Operation.API_CREATABLE_TYPES:
            raise serializers.ValidationError("error : OPERATION_TYPE_NOT_AUTHORIZED")
        return value

    def validate(self, data):
        if data.get("objective_sector") and data.get("type") != Operation.TENEUR:
            raise serializers.ValidationError(
                {"declared_sector": "objective_sector ne peut être défini que pour les opérations de type TENEUR"}
            )
        return data

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context.get("request")
            entity_id = request.entity.id
            selected_lots = validated_data.pop("lots")
            declaration_year = self.context.get("declaration_year")

            OperationService.perform_checks_before_create(
                request, entity_id, selected_lots, validated_data, declaration_year
            )

            # Fetch emission rates from the oldest OperationDetail for each lot
            lot_ids = [lot["id"] for lot in selected_lots]
            emissions_by_lot = OperationService.get_emission_rates_by_lot(lot_ids)

            OperationService.define_operation_status(validated_data)

            # Create the operation
            operation = Operation.objects.create(**validated_data)

            # Create the details using server-side emission rates
            detail_operations_data = []
            for lot in selected_lots:
                detail_operations_data.append(
                    {
                        "operation": operation,
                        "lot_id": lot["id"],
                        "volume": truncate(lot["volume"]),
                        "emission_rate_per_mj": emissions_by_lot[lot["id"]],
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
