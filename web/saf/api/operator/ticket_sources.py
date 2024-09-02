# /api/saf/operator/ticket-sources

import traceback
from math import floor

from django import forms
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.expressions import F

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.utils import MultipleValueField
from saf.models import SafTicketSource
from saf.serializers import SafTicketSourceSerializer
from saf.serializers.saf_ticket_source import export_ticket_sources_to_excel


class SafTicketSourceError:
    TICKET_SOURCE_LISTING_FAILED = "TICKET_SOURCE_LISTING_FAILED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


class TicketSourceFilterForm(forms.Form):
    entity_id = forms.IntegerField()
    status = forms.CharField()
    year = forms.IntegerField()
    periods = MultipleValueField(coerce=int, required=False)
    feedstocks = MultipleValueField(coerce=str, required=False)
    clients = MultipleValueField(coerce=str, required=False)
    suppliers = MultipleValueField(coerce=str, required=False)
    countries_of_origin = MultipleValueField(coerce=str, required=False)
    production_sites = MultipleValueField(coerce=str, required=False)
    delivery_sites = MultipleValueField(coerce=str, required=False)
    search = forms.CharField(required=False)


class TicketSourceSortForm(forms.Form):
    sort_by = forms.CharField(required=False)
    order = forms.CharField(required=False)
    from_idx = forms.IntegerField(initial=0)
    limit = forms.IntegerField(initial=25)


@check_user_rights()
def get_ticket_sources(request, *args, **kwargs):
    filter_form = TicketSourceFilterForm(request.GET)
    sort_form = TicketSourceSortForm(request.GET)

    if not filter_form.is_valid() or not sort_form.is_valid():
        return ErrorResponse(400, SafTicketSourceError.MALFORMED_PARAMS, {**filter_form.errors, **sort_form.errors})

    export = "export" in request.GET

    sort_by = sort_form.cleaned_data["sort_by"]
    order = sort_form.cleaned_data["order"]
    from_idx = sort_form.cleaned_data["from_idx"]
    limit = sort_form.cleaned_data["limit"]

    try:
        ticket_sources = find_ticket_sources(**filter_form.cleaned_data)

        if export:
            file = export_ticket_sources_to_excel(ticket_sources)
            return ExcelResponse(file)

        ticket_sources = sort_ticket_sources(ticket_sources, sort_by, order)

        paginator = Paginator(ticket_sources, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)

        ids = ticket_sources.values_list("id", flat=True)
        serialized = SafTicketSourceSerializer(page.object_list, many=True)

        return SuccessResponse(
            {
                "saf_ticket_sources": serialized.data,
                "ids": list(ids),
                "from": from_idx,
                "returned": len(serialized.data),
                "total": len(ids),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketSourceError.TICKET_SOURCE_LISTING_FAILED)


def find_ticket_sources(**filters):
    ticket_sources = (
        SafTicketSource.objects.select_related(
            "feedstock",
            "biofuel",
            "country_of_origin",
            "carbure_production_site",
        )
        .prefetch_related("saf_tickets")
        .prefetch_related("saf_tickets__client")
    )

    if filters["entity_id"]:
        ticket_sources = ticket_sources.filter(added_by_id=filters["entity_id"])

    if filters["year"]:
        ticket_sources = ticket_sources.filter(year=filters["year"])

    if filters["periods"]:
        ticket_sources = ticket_sources.filter(delivery_period__in=filters["periods"])

    if filters["feedstocks"]:
        ticket_sources = ticket_sources.filter(feedstock__code__in=filters["feedstocks"])

    if filters["clients"]:
        ticket_sources = ticket_sources.filter(saf_tickets__client__name__in=filters["clients"])

    if filters["suppliers"]:
        suppliers = filters["suppliers"]
        ticket_sources = ticket_sources.filter(
            Q(parent_lot__carbure_supplier__name__in=suppliers)
            | Q(parent_lot__unknown_supplier__in=suppliers)
            | Q(parent_ticket__supplier__name__in=suppliers)
        )

    if filters["countries_of_origin"]:
        ticket_sources = ticket_sources.filter(country_of_origin__code_pays__in=filters["countries_of_origin"])

    if filters["production_sites"]:
        ticket_sources = ticket_sources.filter(carbure_production_site__name__in=filters["production_sites"])

    if filters["delivery_sites"]:
        ticket_sources = ticket_sources.filter(parent_lot__carbure_delivery_site__name__in=filters["delivery_sites"])

    if filters["status"] == "AVAILABLE":
        ticket_sources = ticket_sources.filter(assigned_volume__lt=F("total_volume"))
    elif filters["status"] == "HISTORY":
        ticket_sources = ticket_sources.filter(assigned_volume__gte=F("total_volume"))
    else:
        raise Exception("Status '%s' does not exist for ticket sources" % filters["status"])

    if filters["search"] is not None:
        ticket_sources = ticket_sources.filter(
            Q(carbure_id__icontains=filters["search"])
            | Q(saf_tickets__client__name__icontains=filters["search"])
            | Q(feedstock__name__icontains=filters["search"])
            | Q(biofuel__name__icontains=filters["search"])
            | Q(country_of_origin__name__icontains=filters["search"])
            | Q(carbure_production_site__name__icontains=filters["search"])
            | Q(unknown_production_site__icontains=filters["search"])
        )

    return ticket_sources


def sort_ticket_sources(ticket_sources, sort_by, order):
    sortable_columns = {
        "volume": "total_volume",
        "period": "delivery_period",
        "feedstock": "feedstock__code",
        "ghg_reduction": "ghg_reduction",
    }

    column = sortable_columns.get(sort_by, "created_at")

    if order == "desc":
        return ticket_sources.order_by("-%s" % column)
    else:
        return ticket_sources.order_by(column)
