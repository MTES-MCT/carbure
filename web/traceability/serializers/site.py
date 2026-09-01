from rest_framework import serializers

from core.serializers import CountrySerializer
from transactions.models import Site


class ActionSiteSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Site
        fields = ["id", "name", "site_type", "country"]
