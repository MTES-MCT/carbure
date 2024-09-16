import datetime

from rest_framework import serializers

from core.excel import export_to_excel
from core.models import CarbureLot
from core.serializers import CarbureLotPublicSerializer, EntityPreviewSerializer, ProductionSiteSerializer
from doublecount.serializers import BiofuelSerializer, CountrySerializer, FeedStockSerializer
from saf.models import SafTicketSource


class SafTicketSourceParentLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbureLot
        fields = [
            "id",
            "carbure_id",
        ]


class SafTicketSourceSerializer(serializers.ModelSerializer):
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
        ]

    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    assigned_tickets = serializers.SerializerMethodField()
    parent_lot = SafTicketSourceParentLotSerializer(read_only=True)

    def get_assigned_tickets(self, obj):
        from .saf_ticket import SafTicketPreviewSerializer  # noqa: E402

        return SafTicketPreviewSerializer(obj.saf_tickets, many=True).data


class SafTicketSourceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafTicketSource
        fields = [
            "id",
            "carbure_id",
            "year",
            "delivery_period",
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
            "parent_lot",
        ]

    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    added_by = EntityPreviewSerializer(read_only=True)
    carbure_producer = EntityPreviewSerializer(read_only=True)
    carbure_production_site = ProductionSiteSerializer(read_only=True)
    assigned_tickets = serializers.SerializerMethodField()
    parent_lot = CarbureLotPublicSerializer()

    def get_assigned_tickets(self, obj):
        from .saf_ticket import SafTicketPreviewSerializer  # noqa: E402

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


def export_ticket_sources_to_excel(tickets):
    today = datetime.datetime.today()
    location = "/tmp/carbure_saf_ticket_sources_%s.xlsx" % (today.strftime("%Y%m%d_%H%M"))

    return export_to_excel(
        location,
        [
            {
                "label": "tickets",
                "rows": SafTicketSourceDetailsSerializer(tickets, many=True).data,
                "columns": [
                    {"label": "carbure_id", "value": "carbure_id"},
                    {"label": "year", "value": "year"},
                    {"label": "delivery_period", "value": "delivery_period"},
                    {"label": "total_volume", "value": "total_volume"},
                    {"label": "assigned_volume", "value": "assigned_volume"},
                    {"label": "biofuel", "value": "biofuel.name"},
                    {"label": "feedstock", "value": "feedstock.name"},
                    {"label": "country_of_origin", "value": "country_of_origin.name"},
                    {"label": "producer", "value": get_producer},
                    {"label": "production_site", "value": get_production_site},
                    {"label": "production_site_commissioning_date", "value": "production_site_commissioning_date"},
                    {"label": "supplier", "value": "parent_lot.carbure_supplier.name"},
                    {"label": "delivery_site", "value": "parent_lot.carbure_delivery_site.name"},
                    {"label": "eec", "value": "eec"},
                    {"label": "el", "value": "el"},
                    {"label": "ep", "value": "ep"},
                    {"label": "etd", "value": "etd"},
                    {"label": "eu", "value": "eu"},
                    {"label": "esca", "value": "esca"},
                    {"label": "eccs", "value": "eccs"},
                    {"label": "eccr", "value": "eccr"},
                    {"label": "eee", "value": "eee"},
                    {"label": "ghg_total", "value": "ghg_total"},
                    {"label": "ghg_reference", "value": "ghg_reference"},
                    {"label": "ghg_reduction", "value": "ghg_reduction"},
                ],
            }
        ],
    )


def get_producer(obj):
    if "carbure_producer" in obj and obj["carbure_producer"]:
        return obj["carbure_producer"]["name"]
    elif "unknown_producer" in obj and obj["unknown_producer"]:
        return obj["unknown_producer"]


def get_production_site(obj):
    if "carbure_production_site" in obj and obj["carbure_production_site"]:
        return obj["carbure_production_site"]["name"]
    elif "unknown_production_site" in obj and obj["unknown_production_site"]:
        return obj["unknown_production_site"]
