from rest_framework import serializers

from tiruert.serializers.balance import BalanceQuantitySerializer


class ElecBalanceSerializer(serializers.Serializer):
    initial_balance = serializers.SerializerMethodField()
    available_balance = serializers.FloatField()
    quantity = BalanceQuantitySerializer()
    pending_teneur = serializers.FloatField()
    declared_teneur = serializers.FloatField()
    pending_operations = serializers.IntegerField()

    def get_initial_balance(self, instance) -> float:
        return instance["available_balance"] - instance["quantity"]["credit"] + instance["quantity"]["debit"]
