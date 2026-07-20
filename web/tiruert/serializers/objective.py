from rest_framework import serializers

from core.models import Entity, MatierePremiere
from tiruert.models.objective import Objective
from tiruert.models.operation import Operation
from tiruert.serializers.fields import TruncatedFloatField


class ObjectiveSerializer(serializers.Serializer):
    target_mj = TruncatedFloatField(decimal_places=0, allow_null=True)
    target_type = serializers.ChoiceField(choices=Objective.TARGET_TYPES, allow_null=True)
    penalty = serializers.IntegerField(allow_null=True)
    target_percent = serializers.FloatField(allow_null=True)


class ObjectiveSectorSerializer(serializers.Serializer):
    code = serializers.ChoiceField(choices=Operation.SECTOR_CODE_CHOICES)
    pending_teneur = TruncatedFloatField(decimal_places=0)
    declared_teneur = TruncatedFloatField(decimal_places=0)
    available_balance = TruncatedFloatField(decimal_places=0)
    unit = serializers.CharField()
    energy_basis = TruncatedFloatField(decimal_places=0, default=0)
    objective = ObjectiveSerializer()


class ObjectiveCategorySerializer(serializers.Serializer):
    code = serializers.ChoiceField(choices=MatierePremiere.MP_CATEGORIES)
    pending_teneur = TruncatedFloatField(decimal_places=0)
    declared_teneur = TruncatedFloatField(decimal_places=0)
    available_balance = TruncatedFloatField(decimal_places=0)
    unit = serializers.CharField()
    objective = ObjectiveSerializer()


class MainObjectiveSerializer(serializers.Serializer):
    available_balance = TruncatedFloatField()  # tCO2
    target = TruncatedFloatField()  # tCO2
    pending_teneur = TruncatedFloatField()  # tCO2
    declared_teneur = TruncatedFloatField()  # tCO2
    unit = serializers.CharField()  # tCO2
    penalty = serializers.IntegerField()  # centimes euros
    target_percent = serializers.FloatField()  # tCO2
    energy_basis = TruncatedFloatField(decimal_places=0)  # MJ


class ObjectiveOutputSerializer(serializers.Serializer):
    main = MainObjectiveSerializer()
    sectors = serializers.ListField(child=ObjectiveSectorSerializer())
    categories = serializers.ListField(child=ObjectiveCategorySerializer())


class ObjectiveInputSerializer(serializers.Serializer):
    entity_id = serializers.IntegerField(required=True)
    year = serializers.IntegerField(required=True)
    selected_entity_id = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.filter(is_tiruert_liable=True), required=False, allow_null=True, default=None
    )
