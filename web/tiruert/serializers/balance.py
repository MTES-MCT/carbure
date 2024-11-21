from rest_framework import serializers

from tiruert.models import Operation


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = [
            "customs_category",
            "biofuel",
            "credit",
            "debit",
        ]

    credit = serializers.FloatField()
    debit = serializers.FloatField()

    @classmethod
    def transform_balance_data(cls, balance_dict, entity_id):
        balance_list = [
            {
                "customs_category": key[0],
                "biofuel": key[1],
                "credit": value["credit"],
                "debit": value["debit"],
            }
            for key, value in balance_dict.items()
        ]
        return balance_list


class LotSerializer(serializers.Serializer):
    lot = serializers.IntegerField()
    credit = serializers.FloatField()
    debit = serializers.FloatField()


class BalanceByLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = [
            "customs_category",
            "biofuel",
            "lots",
        ]

    lots = LotSerializer(many=True, required=False)

    @classmethod
    def transform_balance_data(cls, balance_dict, entity_id):
        # Group by customs_category and biofuel, and display balance by lot
        grouped_balance = {}
        for key, value in balance_dict.items():
            customs_cat, biofuel, lot_id = key
            group_key = (customs_cat, biofuel)

            if group_key not in grouped_balance:
                grouped_balance[group_key] = {
                    "customs_category": customs_cat,
                    "biofuel": biofuel,
                    "lots": [],
                }

            grouped_balance[group_key]["lots"].append(
                {"lot": lot_id, "credit": value["credit"], "debit": value["debit"]},
            )

        return list(grouped_balance.values())
