from django.core.exceptions import ValidationError
from rest_framework import serializers

from core.models import Pays
from transactions.models import Depot


class DepotSerializer(serializers.ModelSerializer):
    country_code = serializers.SlugRelatedField(slug_field="code_pays", queryset=Pays.objects.all(), write_only=True)

    class Meta:
        model = Depot
        fields = "__all__"

    def create(self, validated_data):
        validated_data["country"] = validated_data.pop("country_code")
        validated_data["is_enabled"] = False

        depot_instance = Depot(**validated_data)

        try:
            depot_instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        depot_instance.save()
        return depot_instance
