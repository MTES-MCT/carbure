from rest_framework import serializers

from saf.models.constants import SAF_BIOFUEL_TYPES
from tiruert.models import Operation


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = [
            "sector",
            "customs_category",
            "biofuel",
            "pending",
            "volume",
            "ghg",
        ]

    sector = serializers.SerializerMethodField()
    volume = serializers.DictField(child=serializers.DecimalField(max_digits=20, decimal_places=2))
    ghg = serializers.DictField(child=serializers.DecimalField(max_digits=20, decimal_places=2))
    pending = serializers.IntegerField()

    def get_sector(self, instance):
        if instance.get("biofuel").compatible_essence:
            return "ESSENCE"
        elif instance.get("biofuel").compatible_diesel:
            return "DIESEL"
        elif instance.get("biofuel").code in SAF_BIOFUEL_TYPES:
            return "SAF"

    @classmethod
    def transform_balance_data(cls, balance_dict, entity_id):
        balance_list = [
            {
                "customs_category": key[0],
                "biofuel": key[1],
                "volume": {
                    "credit": value["volume"]["credit"],
                    "debit": value["volume"]["debit"],
                },
                "ghg": {
                    "credit": value["ghg"]["credit"],
                    "debit": value["ghg"]["debit"],
                },
                "pending": value["pending"],
            }
            for key, value in balance_dict.items()
        ]
        return balance_list


class LotSerializer(serializers.Serializer):
    lot = serializers.IntegerField()
    volume = serializers.DictField(child=serializers.DecimalField(max_digits=20, decimal_places=2))
    ghg = serializers.DictField(child=serializers.DecimalField(max_digits=20, decimal_places=2))


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
                {
                    "lot": lot_id,
                    "volume": {
                        "credit": value["volume"]["credit"],
                        "debit": value["volume"]["debit"],
                    },
                    "ghg": {
                        "credit": value["ghg"]["credit"],
                        "debit": value["ghg"]["debit"],
                    },
                },
            )

        return list(grouped_balance.values())
