import datetime

from django.utils.translation import gettext as _
from rest_framework import serializers

from core.excel import export_to_excel
from core.models import Biocarburant
from core.serializers import AirportSerializer, EntityPreviewSerializer, ProductionSiteSerializer
from doublecount.serializers import BiofuelSerializer, CountrySerializer, FeedStockSerializer
from saf.models import SafTicket
from transactions.models import Airport


class SafTicketSerializer(serializers.ModelSerializer):
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
            "ets_status",
        ]

    feedstock = FeedStockSerializer(read_only=True)
    biofuel = BiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    supplier = serializers.SlugRelatedField(read_only=True, slug_field="name")
    client = serializers.SlugRelatedField(read_only=True, slug_field="name")


class SafBiofuelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biocarburant
        fields = ["name", "name_en", "code", "pci_kg", "pci_litre", "masse_volumique"]


class SafTicketDetailsSerializer(serializers.ModelSerializer):
    from .saf_ticket_source import SafTicketSourcePreviewSerializer  # noqa: E402

    class Meta:
        model = SafTicket
        fields = [
            "id",
            "carbure_id",
            "year",
            "assignment_period",
            "status",
            "created_at",
            "supplier",
            "client",
            "free_field",
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
            "client_comment",
            "parent_ticket_source",
            "shipping_method",
            "reception_airport",
            "consumption_type",
            "ets_status",
        ]

    feedstock = FeedStockSerializer(read_only=True)
    biofuel = SafBiofuelSerializer(read_only=True)
    country_of_origin = CountrySerializer(read_only=True)
    carbure_producer = EntityPreviewSerializer(read_only=True)
    carbure_production_site = ProductionSiteSerializer(read_only=True)
    parent_ticket_source = SafTicketSourcePreviewSerializer(read_only=True)
    supplier = serializers.SlugRelatedField(read_only=True, slug_field="name")
    client = serializers.SlugRelatedField(read_only=True, slug_field="name")
    reception_airport = AirportSerializer(read_only=True)


def export_tickets_to_excel(tickets):
    today = datetime.datetime.today()
    location = "/tmp/carbure_saf_tickets_%s.xlsx" % (today.strftime("%Y%m%d_%H%M"))

    return export_to_excel(
        location,
        [
            {
                "label": _("tickets"),
                "rows": SafTicketDetailsSerializer(tickets, many=True).data,
                "columns": [
                    {"label": "carbure_id", "value": "carbure_id"},
                    {"label": "year", "value": "year"},
                    {"label": "assignment_period", "value": "assignment_period"},
                    {"label": "agreement_reference", "value": "agreement_reference"},
                    {"label": "agreement_date", "value": "agreement_date"},
                    {"label": "volume", "value": "volume"},
                    {"label": "biofuel", "value": "biofuel.name"},
                    {"label": "feedstock", "value": "feedstock.name"},
                    {"label": "country_of_origin", "value": "country_of_origin.name"},
                    {"label": "supplier", "value": "supplier"},
                    {"label": "client", "value": "client"},
                    {"label": "producer", "value": get_producer},
                    {"label": "production_site", "value": get_production_site},
                    {"label": "production_site_commissioning_date", "value": "production_site_commissioning_date"},
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
                    {"label": "ghg_reduction", "value": "ghg_reduction"},
                    {"label": "free_field", "value": "free_field"},
                    {"label": "reception_airport", "value": "reception_airport.name"},
                    {"label": "reception_airport_icao", "value": "reception_airport.icao_code"},
                    {"label": "biofuel_pci_kg", "value": "biofuel.pci_kg"},
                    {"label": "biofuel_pci_litre", "value": "biofuel.pci_litre"},
                    {"label": "biofuel_masse_volumique", "value": "biofuel.masse_volumique"},
                ],
            },
            {
                "label": _("aeroports"),
                "rows": AirportSerializer(Airport.objects.all(), many=True).data,
                "columns": [
                    {"label": "name", "value": "name"},
                    {"label": "icao_code", "value": "icao_code"},
                    {"label": "city", "value": "city"},
                    {"label": "country", "value": "country.name"},
                ],
            },
        ],
    )


def get_producer(obj):
    if obj.get("carbure_producer"):
        return obj["carbure_producer"]["name"]
    elif obj.get("unknown_producer"):
        return obj["unknown_producer"]
    else:
        return ""


def get_production_site(obj):
    if obj.get("carbure_production_site"):
        return obj["carbure_production_site"]["name"]
    elif obj.get("unknown_production_site"):
        return obj["unknown_production_site"]
    else:
        return ""
