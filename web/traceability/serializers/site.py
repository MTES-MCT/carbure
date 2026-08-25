from rest_framework import serializers

from transactions.models import Site


class ActionSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ["id", "name", "site_type"]
