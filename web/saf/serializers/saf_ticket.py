from rest_framework import serializers

from saf.models import SafTicket
from doublecount.serializers import BiofuelSerializer, CountrySerializer, FeedStockSerializer


class SafTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicket
        fields = [
            "id",
            "carbure_id",
            "year",
            "period",
            "status",
            "agreement_date",
            "supplier",
            "client",
            "volume",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "ghg_reduction",
        ]

    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    supplier = serializers.SlugRelatedField(read_only=True, slug_field="name")
    client = serializers.SlugRelatedField(read_only=True, slug_field="name")


class SafTicketPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicket
        fields = [
            "id",
            "carbure_id",
            "client",
            "agreement_date",
            "volume",
            "status",
        ]

    client = serializers.SlugRelatedField(read_only=True, slug_field="name")
