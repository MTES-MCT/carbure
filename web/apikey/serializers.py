from rest_framework import serializers

from apikey.models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ["name"]


class APIKeyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        exclude = ("user",)
