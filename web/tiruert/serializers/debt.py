from rest_framework import serializers

from core.models import Biocarburant, MatierePremiere
from tiruert.models import Operation
from tiruert.serializers.balance import BalanceBiofuelSerializer
from tiruert.serializers.fields import TruncatedFloatField
from tiruert.serializers.operation import OperationLotSerializer


class DebtRepaymentInputSerializer(serializers.Serializer):
    biofuel = serializers.PrimaryKeyRelatedField(queryset=Biocarburant.objects.all())
    customs_category = serializers.ChoiceField(choices=MatierePremiere.MP_CATEGORIES)
    lots = OperationLotSerializer(many=True, allow_empty=False)
    status = serializers.ChoiceField(
        choices=[Operation.VALIDATED, Operation.DRAFT], required=False, default=Operation.VALIDATED
    )


class DebtSummarySerializer(serializers.Serializer):
    biofuel = BalanceBiofuelSerializer()
    customs_category = serializers.ChoiceField(choices=MatierePremiere.MP_CATEGORIES)
    remaining_volume = TruncatedFloatField()
