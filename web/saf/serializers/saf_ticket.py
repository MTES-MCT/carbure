from rest_framework import serializers

from doublecount.serializers import BiofuelSerializer, CountrySerializer, FeedStockSerializer
from core.serializers import EntityPreviewSerializer, ProductionSiteSerializer
from saf.models import SafTicket


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


class SafTicketDetailsSerializer(serializers.ModelSerializer):
    from .saf_ticket_source import SafTicketSourcePreviewSerializer

    class Meta:
        model = SafTicket
        fields = [
            "id",
            "carbure_id",
            "year",
            "period",
            "status",
            "created_at",
            "supplier",
            "client",
            "agreement_date",
            "agreement_reference",
            "volume",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "carbure_producer",
            "unknown_producer",
            "carbure_production_site",
            "unknown_production_site",
            "production_site_commissioning_date",
            "eec",
            "el",
            "ep",
            "etd",
            "eu",
            "esca",
            "eccs",
            "eccr",
            "eee",
            "ghg_reduction",
            "ghg_total",
            "parent_ticket_source",
        ]

    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    supplier = EntityPreviewSerializer(read_only=True)
    client = EntityPreviewSerializer(read_only=True)
    carbure_producer = EntityPreviewSerializer(read_only=True)
    carbure_production_site = ProductionSiteSerializer(read_only=True)
    parent_ticket_source = SafTicketSourcePreviewSerializer(read_only=True)


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
