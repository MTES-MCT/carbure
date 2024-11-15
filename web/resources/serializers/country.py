from rest_framework import serializers

from core.models import Pays


class PaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pays
        fields = ["code_pays", "name", "name_en", "is_in_europe"]
