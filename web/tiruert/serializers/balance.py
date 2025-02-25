from rest_framework import serializers

from core.models import MatierePremiere


class TiruertBiofuelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()


class BalanceSerializer(serializers.Serializer):
    sector = serializers.ChoiceField(choices=["ESSENCE", "DIESEL", "SAF"])
    customs_category = serializers.ChoiceField(choices=MatierePremiere.MP_CATEGORIES, required=False)
    biofuel = TiruertBiofuelSerializer(required=False)
    initial_balance = serializers.FloatField()
    available_balance = serializers.SerializerMethodField()
    final_balance = serializers.SerializerMethodField()
    quantity = serializers.DictField(child=serializers.FloatField())
    # avg_emission_rate_per_mj = serializers.FloatField()
    teneur = serializers.FloatField()
    yearly_teneur = serializers.FloatField(required=False)
    pending = serializers.IntegerField()
    unit = serializers.CharField()

    def to_representation(self, instance):
        # Overrides the default representation to remove fields with null values.
        representation = super().to_representation(instance)
        return {key: value for key, value in representation.items() if value is not None}

    def get_available_balance(self, instance) -> float:
        return self.calcul_available_balance(instance)

    def get_final_balance(self, instance) -> float:
        return self.calcul_available_balance(instance) - instance["teneur"]

    def calcul_available_balance(self, instance) -> float:
        return instance["initial_balance"] + instance["quantity"]["credit"] - instance["quantity"]["debit"]


class LotSerializer(serializers.Serializer):
    lot = serializers.IntegerField()
    volume = serializers.DictField(child=serializers.FloatField())
    emission_rate_per_mj = serializers.FloatField()


class BalanceByLotSerializer(serializers.Serializer):
    customs_category = serializers.CharField(required=False, allow_null=True)
    biofuel = serializers.CharField(required=False, allow_null=True)
    lots = LotSerializer(many=True, required=False)

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


class DepotSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    volume = serializers.DictField(child=serializers.FloatField())
    unit = serializers.CharField(required=False)


class BalanceByDepotSerializer(serializers.Serializer):
    customs_category = serializers.CharField()
    biofuel = TiruertBiofuelSerializer()
    depots = DepotSerializer(many=True)

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
                    "volume": {
                        "credit": value["quantity"]["credit"],
                        "debit": value["quantity"]["debit"],
                    },
                    "unit": value["unit"],
                },
            )

        return list(grouped_balance.values())
