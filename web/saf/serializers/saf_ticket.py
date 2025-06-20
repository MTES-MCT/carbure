from rest_framework import serializers

from core.serializers import AirportSerializer, EntityPreviewSerializer, ProductionSiteSerializer
from doublecount.serializers import BiofuelSerializer, CountrySerializer, FeedStockSerializer
from saf.models import SafTicket
from saf.models.saf_ticket_source import SafTicketSource


class SafParentTicketSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicketSource
        fields = [
            "id",
            "carbure_id",
            "total_volume",
            "assigned_volume",
        ]


class SafTicketPreviewSerializer(serializers.ModelSerializer):
    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    supplier = serializers.SlugRelatedField(read_only=True, slug_field="name")
    client = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = SafTicket
        fields = [
            "id",
            "carbure_id",
            "year",
            "assignment_period",
            "status",
            "agreement_date",
            "supplier",
            "client",
            "volume",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "ghg_reduction",
            "consumption_type",
            "ets_status",
            "created_at",
        ]


class SafTicketSerializer(SafTicketPreviewSerializer):
    carbure_producer = EntityPreviewSerializer(read_only=True)
    carbure_production_site = ProductionSiteSerializer(read_only=True)
    parent_ticket_source = SafParentTicketSourceSerializer(read_only=True)
    reception_airport = AirportSerializer(read_only=True)

    class Meta:
        model = SafTicket
        fields = SafTicketPreviewSerializer.Meta.fields + [
            "free_field",
            "agreement_reference",
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
            "ghg_total",
            "client_comment",
            "parent_ticket_source",
            "shipping_method",
            "reception_airport",
        ]
