from rest_framework import serializers

from core.models import MatierePremiere
from tiruert.serializers.balance import BalanceBiofuelSerializer
from tiruert.serializers.fields import TruncatedFloatField


class DebtSummarySerializer(serializers.Serializer):
    biofuel = BalanceBiofuelSerializer()
    customs_category = serializers.ChoiceField(choices=MatierePremiere.MP_CATEGORIES)
    remaining_volume = TruncatedFloatField()
