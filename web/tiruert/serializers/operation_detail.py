from rest_framework import serializers

from tiruert.models import OperationDetail


class OperationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationDetail
        fields = ["lot", "volume", "emission_rate_per_mj"]
