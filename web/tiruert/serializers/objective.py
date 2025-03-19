from rest_framework import serializers

# from tiruert.models import MacFossilFuel


class QuantitySerializer(serializers.Serializer):
    credit = serializers.FloatField()
    debit = serializers.FloatField()


class ObjectiveSerializer(serializers.Serializer):
    target_mj = serializers.FloatField()
    target_type = serializers.CharField()


class SectorCategorySerializer(serializers.Serializer):
    # quantity = QuantitySerializer()
    code = serializers.CharField()
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
    sectors = serializers.ListField(child=SectorCategorySerializer())
    categories = serializers.ListField(child=SectorCategorySerializer())
