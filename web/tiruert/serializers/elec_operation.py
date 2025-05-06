from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from tiruert.models import ElecOperation
from tiruert.services.elec_operation import ElecOperationService


class ElecOperationEntitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class BaseElecOperationSerializer(serializers.ModelSerializer):
    credited_entity = ElecOperationEntitySerializer()
    debited_entity = ElecOperationEntitySerializer()
    type = serializers.SerializerMethodField()
    avoided_emissions = serializers.FloatField()

    def get_type(self, instance: ElecOperation) -> str:
        entity_id = self.context.get("entity_id")
        if instance.is_acquisition(entity_id):
            return ElecOperation.ACQUISITION
        else:
            return instance.type


class ElecOperationListSerializer(BaseElecOperationSerializer):
    class Meta:
        model = ElecOperation
        fields = [
            "id",
            "type",
            "status",
            "credited_entity",
            "debited_entity",
            "quantity",
            "created_at",
        ]


class ElecOperationSerializer(BaseElecOperationSerializer):
    class Meta:
        model = ElecOperation
        fields = [
            "id",
            "type",
            "status",
            "credited_entity",
            "debited_entity",
            "quantity",
            "created_at",
            "avoided_emissions",
        ]


class ElecOperationInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecOperation
        fields = [
            "type",
            "credited_entity",
            "debited_entity",
            "quantity",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if validated_data.get("debited_entity") != request.entity:
            raise serializers.ValidationError(_("Only debit operations can be created"))
        ElecOperationService.perform_checks_before_create(request, validated_data)
        return super().create(validated_data)


class ElecOperationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElecOperation
        fields = [
            "type",
            "credited_entity",
            "debited_entity",
            "quantity",
        ]

    def update(self, instance, validated_data):
        request = self.context.get("request")
        entity = request.entity

        if instance.debited_entity != entity:
            raise serializers.ValidationError(_("Only debit operations can be updated"))

        allowed_types = [ElecOperation.CESSION, ElecOperation.TENEUR]
        allowed_statuses = [ElecOperation.PENDING, ElecOperation.REJECTED]
        if instance.type not in allowed_types or instance.status not in allowed_statuses:
            raise serializers.ValidationError(_("Operation cannot be modified anymore"))

        if "debited_entity" in validated_data and validated_data["debited_entity"] != entity:
            raise serializers.ValidationError(_("Cannot modify debited entity"))

        ElecOperationService.perform_checks_before_create(request, validated_data, instance)
        return super().update(instance, validated_data)
