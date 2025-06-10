from rest_framework import serializers

from core.models import Entity, MatierePremiere
from tiruert.models.operation import Operation


class QuantitySerializer(serializers.Serializer):
    credit = serializers.FloatField()
    debit = serializers.FloatField()


class ObjectiveSerializer(serializers.Serializer):
    target_mj = serializers.FloatField()
    target_type = serializers.CharField()
    penalty = serializers.IntegerField()
    target_percent = serializers.FloatField()


class ObjectiveSectorSerializer(serializers.Serializer):
    code = serializers.ChoiceField(choices=Operation.SECTOR_CODE_CHOICES)
    pending_teneur = serializers.FloatField()
    declared_teneur = serializers.FloatField()
    available_balance = serializers.FloatField()
    unit = serializers.CharField()
    objective = ObjectiveSerializer()


class ObjectiveCategorySerializer(serializers.Serializer):
    code = serializers.ChoiceField(choices=MatierePremiere.MP_CATEGORIES)
    pending_teneur = serializers.FloatField()
    declared_teneur = serializers.FloatField()
    available_balance = serializers.FloatField()
    unit = serializers.CharField()
    objective = ObjectiveSerializer()


class MainObjectiveSerializer(serializers.Serializer):
    available_balance = serializers.FloatField()
    target = serializers.FloatField()
    pending_teneur = serializers.FloatField()
    declared_teneur = serializers.FloatField()
    unit = serializers.CharField()
    penalty = serializers.IntegerField()
    target_percent = serializers.FloatField()
    energy_basis = serializers.FloatField()


class ObjectiveOutputSerializer(serializers.Serializer):
    main = MainObjectiveSerializer()
    sectors = serializers.ListField(child=ObjectiveSectorSerializer())
    categories = serializers.ListField(child=ObjectiveCategorySerializer())


class ObjectiveInputSerializer(serializers.Serializer):
    entity_id = serializers.IntegerField(required=True)
    year = serializers.IntegerField(required=True)
    date_from = serializers.DateField(required=True)
    date_to = serializers.DateField(required=False)


class ObjectiveAdminInputSerializer(ObjectiveInputSerializer):
    selected_entity_id = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.all(), required=True)
