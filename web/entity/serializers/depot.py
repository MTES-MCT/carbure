from rest_framework import serializers
from core.models import Depot


class DepotSerializer(serializers.ModelSerializer):

    class Meta:
        model = Depot
        fields = "__all__"
