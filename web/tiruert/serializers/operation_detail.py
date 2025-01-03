from rest_framework import serializers

from tiruert.models import OperationDetail


class OperationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationDetail
        fields = ["lot", "volume", "saved_ghg"]