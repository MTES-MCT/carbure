from rest_framework import serializers

from core.models import MatierePremiere
from tiruert.models.operation import Operation


class BalanceBiofuelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    renewable_energy_share = serializers.FloatField()


class BalanceQuantitySerializer(serializers.Serializer):
    credit = serializers.FloatField(default=0.0)
    debit = serializers.FloatField(default=0.0)


class BaseBalanceSerializer(serializers.Serializer):
    sector = serializers.ChoiceField(choices=Operation.SECTOR_CODE_CHOICES)
    initial_balance = serializers.SerializerMethodField()
    available_balance = serializers.FloatField()
    quantity = BalanceQuantitySerializer()
    pending_teneur = serializers.FloatField()
    declared_teneur = serializers.FloatField()
    pending_operations = serializers.IntegerField()
    unit = serializers.CharField()

    def get_initial_balance(self, instance) -> float:
        return instance["available_balance"] - instance["quantity"]["credit"] + instance["quantity"]["debit"]


class BalanceSerializer(BaseBalanceSerializer):
    customs_category = serializers.ChoiceField(choices=MatierePremiere.MP_CATEGORIES)
    biofuel = BalanceBiofuelSerializer()
    ghg_reduction_min = serializers.FloatField()
    ghg_reduction_max = serializers.FloatField()
    saved_emissions = serializers.FloatField()


class BalanceBySectorSerializer(BaseBalanceSerializer):
    pass


class BalanceLotSerializer(serializers.Serializer):
    lot = serializers.IntegerField()
    available_balance = serializers.FloatField()
    volume = BalanceQuantitySerializer()
    emission_rate_per_mj = serializers.FloatField()


class BalanceByLotSerializer(serializers.Serializer):
    customs_category = serializers.CharField(required=False, allow_null=True)
    biofuel = serializers.CharField(required=False, allow_null=True)
    lots = BalanceLotSerializer(many=True, required=False)

    @staticmethod
    def prepare_data(balance_dict):
        # Group by customs_category and biofuel, and display balance by lot
        grouped_balance = {}

        for key, value in balance_dict.items():
            sector, customs_cat, biofuel, lot_id = key
            group_key = (customs_cat, biofuel)

            if group_key not in grouped_balance:
                grouped_balance[group_key] = {
                    "customs_category": customs_cat,
                    "biofuel": biofuel,
                    "available_balance": 0,
                    "lots": [],
                }

            grouped_balance[group_key]["lots"].append(
                {
                    "lot": lot_id,
                    "available_balance": value["available_balance"],
                    "volume": {
                        "credit": value["quantity"]["credit"],
                        "debit": value["quantity"]["debit"],
                    },
                    "emission_rate_per_mj": value["emission_rate_per_mj"],
                },
            )

            # Sum up the available_balance for all lots
            grouped_balance[group_key]["available_balance"] += value["available_balance"]

        return list(grouped_balance.values())


class BalanceDepotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    quantity = BalanceQuantitySerializer()
    unit = serializers.CharField(required=False)


class BalanceByDepotSerializer(serializers.Serializer):
    customs_category = serializers.CharField()
    biofuel = BalanceBiofuelSerializer()
    depots = BalanceDepotSerializer(many=True)

    @staticmethod
    def prepare_data(balance_dict):
        # Group by customs_category and biofuel, and display balance by depot
        grouped_balance = {}

        for key, value in balance_dict.items():
            sector, customs_cat, biofuel, depot = key
            group_key = (customs_cat, biofuel)

            if group_key not in grouped_balance:
                grouped_balance[group_key] = {
                    "customs_category": customs_cat,
                    "biofuel": value["biofuel"],
                    "available_balance": 0,
                    "depots": [],
                }

            grouped_balance[group_key]["depots"].append(
                {
                    "id": depot.id,
                    "name": depot.name,
                    "quantity": {
                        "credit": value["quantity"]["credit"],
                        "debit": value["quantity"]["debit"],
                    },
                    "unit": value["unit"],
                },
            )

            # Sum up the available_balance for all depots
            grouped_balance[group_key]["available_balance"] += value["available_balance"]

        return list(grouped_balance.values())
