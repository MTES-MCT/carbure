from rest_framework import serializers

from core.models import MatierePremiere


class BalanceBiofuelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()


class BalanceQuantitySerializer(serializers.Serializer):
    credit = serializers.FloatField(default=0.0)
    debit = serializers.FloatField(default=0.0)


class BaseBalanceSerializer(serializers.Serializer):
    sector = serializers.ChoiceField(choices=["ESSENCE", "DIESEL", "SAF"])
    initial_balance = serializers.FloatField()
    available_balance = serializers.SerializerMethodField()
    final_balance = serializers.SerializerMethodField()
    quantity = BalanceQuantitySerializer()
    teneur = serializers.FloatField()
    yearly_teneur = serializers.FloatField(required=False)
    pending = serializers.IntegerField()
    unit = serializers.CharField()

    def get_available_balance(self, instance) -> float:
        return self.calcul_available_balance(instance)

    def get_final_balance(self, instance) -> float:
        return self.calcul_available_balance(instance) - instance["teneur"]

    def calcul_available_balance(self, instance) -> float:
        return instance["initial_balance"] + instance["quantity"]["credit"] - instance["quantity"]["debit"]


class BalanceSerializer(BaseBalanceSerializer):
    customs_category = serializers.ChoiceField(choices=MatierePremiere.MP_CATEGORIES)
    biofuel = BalanceBiofuelSerializer()


class BalanceBySectorSerializer(BaseBalanceSerializer):
    pass


class BalanceLotSerializer(serializers.Serializer):
    lot = serializers.IntegerField()
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
                    "lots": [],
                }

            grouped_balance[group_key]["lots"].append(
                {
                    "lot": lot_id,
                    "volume": {
                        "credit": value["quantity"]["credit"],
                        "debit": value["quantity"]["debit"],
                    },
                    "emission_rate_per_mj": value["emission_rate_per_mj"],
                },
            )

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

        return list(grouped_balance.values())
