from rest_framework import serializers

from .saf_ticket import SafTicketPreviewSerializer
from saf.models import SafTicketSource
from doublecount.serializers import BiofuelSerializer, CountrySerializer, FeedStockSerializer


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
        return SafTicketPreviewSerializer(obj.saf_ticket, many=True).data
