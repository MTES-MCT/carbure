from rest_framework import serializers

from tiruert.models import ElecOperation


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
        # TODO one last check to see if creating such an operation is allowed
        return ElecOperation.objects.create(**validated_data)


class ElecOperationUpdateSerializer(BaseElecOperationSerializer):
    class Meta:
        model = ElecOperation
        fields = [
            "type",
            "credited_entity",
            "debited_entity",
            "quantity",
        ]

    # TODO one last check to see if updating this operation is allowed
