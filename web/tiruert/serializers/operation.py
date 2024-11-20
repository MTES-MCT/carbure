from django.db import transaction
from rest_framework import serializers

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
            "customs_category",
            "biofuel",
            "credited_entity",
            "debited_entity",
            "depot",
            "created_at",
            "validity_date",
            "details",
        ]

    def create(self, validated_data):
        details_data = validated_data.pop("details", [])

        with transaction.atomic():
            operation = Operation.objects.create(**validated_data)

            for detail in details_data:
                OperationDetail.objects.create(operation=operation, **detail)

            return operation
