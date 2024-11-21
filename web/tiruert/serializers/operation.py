from django.db import transaction
from rest_framework import serializers

from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.models import Operation, OperationDetail
from tiruert.serializers.operation_detail import OperationDetailSerializer


class OperationSerializer(serializers.ModelSerializer):
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

    def get_sector(self, instance):
        if instance.biofuel.compatible_essence:
            return "ESSENCE"
        elif instance.biofuel.compatible_diesel:
            return "DIESEL"
        elif instance.biofuel.code in SAF_BIOFUEL_TYPES:
            return "SAF"

    def create(self, validated_data):
        details_data = validated_data.pop("details", [])

        with transaction.atomic():
            operation = Operation.objects.create(**validated_data)

            for detail in details_data:
                OperationDetail.objects.create(operation=operation, **detail)

            return operation
