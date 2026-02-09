from rest_framework import serializers

from feedstocks.models import Feedstock


class FeedstocksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedstock
        fields = ["id", "name"]
