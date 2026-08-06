from rest_framework import serializers

from core.utils import truncate
from tiruert.models.elec_operation import ElecOperation
from tiruert.serializers.fields import TruncatedFloatField


class BalanceQuantitySerializer(serializers.Serializer):
    credit = TruncatedFloatField(default=0.0, decimal_places=0)
    debit = TruncatedFloatField(default=0.0, decimal_places=0)


class ElecBalanceSerializer(serializers.Serializer):
    sector = serializers.ChoiceField(choices=[(ElecOperation.SECTOR, ElecOperation.SECTOR)])
    initial_balance = serializers.SerializerMethodField()
    available_balance = TruncatedFloatField(decimal_places=0)
    quantity = BalanceQuantitySerializer()
    pending_teneur = TruncatedFloatField(decimal_places=0)
    declared_teneur = TruncatedFloatField(decimal_places=0)
    pending_operations = serializers.IntegerField()

    def get_initial_balance(self, instance) -> float:
        return truncate(instance["available_balance"] - instance["quantity"]["credit"] + instance["quantity"]["debit"], 0)
