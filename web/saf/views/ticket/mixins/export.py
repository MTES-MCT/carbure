import datetime

from django.utils.translation import gettext as _
from drf_spectacular.utils import OpenApiExample, OpenApiTypes, extend_schema
from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel
from core.models import Entity
from core.models.models import Biocarburant
from core.serializers import AirportSerializer, BiofuelDetailSerializer
from saf.models.constants import SAF_BIOFUEL_TYPES
from saf.serializers.saf_ticket import SafTicketSerializer
from transactions.models.airport import Airport


class ExportActionMixin:
    @extend_schema(
        filters=True,
        examples=[
            OpenApiExample(
                "Example of export response.",
                value="csv file.csv",
                request_only=False,
                response_only=True,
                media_type="application/vnd.ms-excel",
            ),
        ],
        responses={
            (200, "application/vnd.ms-excel"): OpenApiTypes.STR,
        },
    )
    @action(methods=["get"], detail=False)
    def export(self, request, *args, **kwargs):
        entity = Entity.objects.get(pk=request.query_params.get("entity_id"))
        tickets = self.filter_queryset(self.get_queryset())
        file = export_tickets_to_excel(tickets, entity)
        return ExcelResponse(file)


def export_tickets_to_excel(tickets, entity):
    today = datetime.datetime.today()
    location = "/tmp/carbure_saf_tickets_%s.xlsx" % (today.strftime("%Y%m%d_%H%M"))

    ticket_columns = [
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
        {"label": "client_type", "value": "client_type"},
        {"label": "producer", "value": get_producer},
        {"label": "production_site", "value": get_production_site},
        {"label": "production_country", "value": get_production_country},
        {"label": "production_site_commissioning_date", "value": "production_site_commissioning_date"},
        {"label": "origin_depot", "value": "origin_lot_site.name"},
        {"label": "reception_airport", "value": "reception_airport.name"},
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
    ]

    is_airline = entity.entity_type == Entity.AIRLINE
    is_admin = entity.entity_type in [Entity.ADMIN, Entity.EXTERNAL_ADMIN]

    if is_airline or is_admin:
        ticket_columns.append({"label": "ets_status", "value": "ets_status"})

    airports = Airport.objects.all().select_related("country")
    biofuels = Biocarburant.objects.filter(code__in=SAF_BIOFUEL_TYPES)

    result = export_to_excel(
        location,
        [
            {
                "label": _("tickets"),
                "rows": SafTicketSerializer(tickets, many=True).data,
                "columns": ticket_columns,
            },
            {
                "label": _("aeroports"),
                "rows": AirportSerializer(airports, many=True).data,
                "columns": [
                    {"label": "name", "value": "name"},
                    {"label": "icao_code", "value": "icao_code"},
                    {"label": "city", "value": "city"},
                    {"label": "country", "value": "country.name"},
                ],
            },
            {
                "label": _("biocarburants"),
                "rows": BiofuelDetailSerializer(biofuels, many=True).data,
                "columns": [
                    {"label": "name", "value": "name"},
                    {"label": "code", "value": "code"},
                    {"label": "pci_kg", "value": "pci_kg"},
                    {"label": "pci_litre", "value": "pci_litre"},
                    {"label": "masse_volumique", "value": "masse_volumique"},
                ],
            },
        ],
    )

    return result


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


def get_production_country(obj):
    if obj.get("carbure_production_site"):
        return obj.get("carbure_production_site", {}).get("country", {}).get("name", "")
    elif obj.get("production_country"):
        return obj.get("production_country").get("name", "")
    else:
        return ""
