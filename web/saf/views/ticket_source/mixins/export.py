import datetime

from drf_spectacular.utils import OpenApiExample, OpenApiTypes, extend_schema
from rest_framework.decorators import action

from core.excel import ExcelResponse, export_to_excel
from saf.serializers.saf_ticket_source import SafTicketSourceSerializer


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
        tickets = self.filter_queryset(self.get_queryset())
        file = export_ticket_sources_to_excel(tickets)
        return ExcelResponse(file)


def export_ticket_sources_to_excel(tickets):
    today = datetime.datetime.today()
    location = "/tmp/carbure_saf_ticket_sources_%s.xlsx" % (today.strftime("%Y%m%d_%H%M"))

    return export_to_excel(
        location,
        [
            {
                "label": "tickets",
                "rows": SafTicketSourceSerializer(tickets, many=True).data,
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
