from rest_framework import serializers

from core.models import MatierePremiere
from tiruert.models.operation import Operation


class QuantitySerializer(serializers.Serializer):
    credit = serializers.FloatField()
    debit = serializers.FloatField()


class ObjectiveSerializer(serializers.Serializer):
    target_mj = serializers.FloatField()
    target_type = serializers.CharField()


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


class ObjectiveOutputSerializer(serializers.Serializer):
    main = MainObjectiveSerializer()
    sectors = serializers.ListField(child=ObjectiveSectorSerializer())
    categories = serializers.ListField(child=ObjectiveCategorySerializer())
