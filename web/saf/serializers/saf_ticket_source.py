from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import CarbureLot
from core.serializers import CarbureLotPublicSerializer, EntityPreviewSerializer, ProductionSiteSerializer
from doublecount.serializers import BiofuelSerializer, CountrySerializer, FeedStockSerializer
from saf.models import SafTicket, SafTicketSource


class SafParentLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbureLot
        fields = [
            "id",
            "carbure_id",
        ]


class SafParentTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicket
        fields = [
            "id",
            "carbure_id",
        ]


class SafAssignedTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicket
        fields = [
            "id",
            "carbure_id",
            "client",
            "agreement_date",
            "volume",
            "status",
            "created_at",
            "assignment_period",
        ]

    client = serializers.SlugRelatedField(read_only=True, slug_field="name")


class SafTicketSourcePreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicketSource
        fields = [
            "id",
            "carbure_id",
            "year",
            "delivery_period",
            "created_at",
            "total_volume",
            "assigned_volume",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "ghg_reduction",
            "assigned_tickets",
            "parent_lot",
            "parent_ticket",
            "added_by",
        ]

    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    assigned_tickets = serializers.SerializerMethodField()
    parent_lot = SafParentLotSerializer(read_only=True, required=False)
    parent_ticket = SafParentTicketSerializer(required=False)
    added_by = EntityPreviewSerializer(read_only=True)

    @extend_schema_field(SafAssignedTicketSerializer(many=True))
    def get_assigned_tickets(self, obj):
        return SafAssignedTicketSerializer(obj.saf_tickets, many=True).data


class SafTicketSourceSerializer(SafTicketSourcePreviewSerializer):
    class Meta:
        model = SafTicketSource
        fields = SafTicketSourcePreviewSerializer.Meta.fields + [
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

    carbure_producer = EntityPreviewSerializer(read_only=True)
    carbure_production_site = ProductionSiteSerializer(read_only=True)
    parent_lot = CarbureLotPublicSerializer(required=False)
