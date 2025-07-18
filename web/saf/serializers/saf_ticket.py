from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.models import Entity
from core.serializers import AirportSerializer, EntityPreviewSerializer, ProductionSiteSerializer
from doublecount.serializers import BiofuelSerializer, CountrySerializer, FeedStockSerializer
from saf.models import SafTicket
from saf.models.saf_ticket_source import SafTicketSource


class SafRelatedTicketSourceSerializer(serializers.ModelSerializer):
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
    reception_airport = AirportSerializer(read_only=True, required=False)

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
            "reception_airport",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        if not request:
            return data

        entity = request.entity
        is_admin = entity.entity_type in (Entity.ADMIN, Entity.EXTERNAL_ADMIN)
        is_airline = entity.entity_type == Entity.AIRLINE

        if not is_airline and not is_admin:
            data["ets_status"] = None

        return data


class SafTicketSerializer(SafTicketPreviewSerializer):
    carbure_producer = EntityPreviewSerializer(read_only=True)
    carbure_production_site = ProductionSiteSerializer(read_only=True)
    parent_ticket_source = SafRelatedTicketSourceSerializer(read_only=True)
    child_ticket_sources = serializers.SerializerMethodField()

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
            "child_ticket_sources",
        ]

    @extend_schema_field(SafRelatedTicketSourceSerializer(many=True))
    def get_child_ticket_sources(self, obj):
        return SafRelatedTicketSourceSerializer(obj.safticketsource_set, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        if not request:
            return data

        entity = request.entity
        is_admin = entity.entity_type in (Entity.ADMIN, Entity.EXTERNAL_ADMIN)
        is_supplier = instance.supplier_id == entity.id
        is_client = instance.client_id == entity.id

        if not is_supplier and not is_admin:
            data["parent_ticket_source"] = None

        if not is_client and not is_admin:
            data["child_ticket_sources"] = []

        return data
