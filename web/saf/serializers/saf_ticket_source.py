from rest_framework import serializers

from doublecount.serializers import BiofuelSerializer, CountrySerializer, FeedStockSerializer
from core.serializers import ProductionSiteSerializer, EntityPreviewSerializer
from saf.models import SafTicketSource


class SafTicketSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicketSource
        fields = [
            "id",
            "carbure_id",
            "year",
            "period",
            "created_at",
            "total_volume",
            "assigned_volume",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "ghg_reduction",
            "assigned_tickets",
        ]

    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    assigned_tickets = serializers.SerializerMethodField()

    def get_assigned_tickets(self, obj):
        from .saf_ticket import SafTicketPreviewSerializer

        return SafTicketPreviewSerializer(obj.saf_tickets, many=True).data


class SafTicketSourceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicketSource
        fields = [
            "id",
            "carbure_id",
            "year",
            "period",
            "created_at",
            "added_by",
            "total_volume",
            "assigned_volume",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "assigned_tickets",
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
        ]

    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    added_by = EntityPreviewSerializer(read_only=True)
    carbure_producer = EntityPreviewSerializer(read_only=True)
    carbure_production_site = ProductionSiteSerializer(read_only=True)
    assigned_tickets = serializers.SerializerMethodField()

    def get_assigned_tickets(self, obj):
        from .saf_ticket import SafTicketPreviewSerializer

        return SafTicketPreviewSerializer(obj.saf_tickets, many=True).data


class SafTicketSourcePreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicketSource
        fields = [
            "id",
            "carbure_id",
            "total_volume",
            "assigned_volume",
        ]
