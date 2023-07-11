# /api/v5/saf/operator/tickets

from math import floor
import traceback
from django import forms
from django.core.paginator import Paginator
from django.db.models import Q

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from core.utils import MultipleValueField
from saf.models import SafTicket
from saf.serializers import SafTicketSerializer


class SafTicketError:
    TICKET_LISTING_FAILED = "TICKET_LISTING_FAILED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"


class TicketFilterForm(forms.Form):
    entity_id = forms.IntegerField()
    type = forms.CharField()
    status = forms.CharField()
    year = forms.IntegerField()
    periods = MultipleValueField(coerce=int, required=False)
    feedstocks = MultipleValueField(coerce=str, required=False)
    clients = MultipleValueField(coerce=str, required=False)
    suppliers = MultipleValueField(coerce=str, required=False)
    countries_of_origin = MultipleValueField(coerce=str, required=False)
    production_sites = MultipleValueField(coerce=str, required=False)
    search = forms.CharField(required=False)


class TicketSortForm(forms.Form):
    sort_by = forms.CharField(required=False)
    order = forms.CharField(required=False)
    from_idx = forms.IntegerField(initial=0)
    limit = forms.IntegerField(initial=25)


@check_user_rights()
def get_tickets(request, *args, **kwargs):
    filter_form = TicketFilterForm(request.GET)
    sort_form = TicketSortForm(request.GET)

    if not filter_form.is_valid() or not sort_form.is_valid():
        return ErrorResponse(400, SafTicketError.MALFORMED_PARAMS, {**filter_form.errors, **sort_form.errors})

    sort_by = sort_form.cleaned_data["sort_by"]
    order = sort_form.cleaned_data["order"]
    from_idx = sort_form.cleaned_data["from_idx"]
    limit = sort_form.cleaned_data["limit"]

    try:
        tickets = find_tickets(**filter_form.cleaned_data)
        tickets = sort_tickets(tickets, sort_by, order)

        paginator = Paginator(tickets, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)

        ids = tickets.values_list("id", flat=True)
        serialized = SafTicketSerializer(page.object_list, many=True)

        return SuccessResponse(
            {
                "saf_tickets": serialized.data,
                "ids": list(ids),
                "from": from_idx,
                "returned": len(serialized.data),
                "total": len(ids),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafTicketError.TICKET_LISTING_FAILED)


def find_tickets(**filters):
    tickets = SafTicket.objects.select_related(
        "parent_ticket_source",
        "feedstock",
        "biofuel",
        "country_of_origin",
        "carbure_production_site",
        "supplier",
        "client",
    )

    if filters["entity_id"]:
        if filters["type"] == "assigned":
            tickets = tickets.filter(supplier_id=filters["entity_id"])
        elif filters["type"] == "received":
            tickets = tickets.filter(client_id=filters["entity_id"])

    if filters["year"]:
        tickets = tickets.filter(year=filters["year"])

    if filters["periods"]:
        tickets = tickets.filter(assignment_period__in=filters["periods"])

    if filters["feedstocks"]:
        tickets = tickets.filter(feedstock__code__in=filters["feedstocks"])

    if filters["clients"]:
        tickets = tickets.filter(client__name__in=filters["clients"])

    if filters["suppliers"]:
        tickets = tickets.filter(supplier__name__in=filters["suppliers"])

    if filters["countries_of_origin"]:
        tickets = tickets.filter(country_of_origin__code_pays__in=filters["countries_of_origin"])

    if filters["production_sites"]:
        tickets = tickets.filter(carbure_production_site__name__in=filters["production_sites"])

    if filters["status"] == SafTicket.PENDING:
        tickets = tickets.filter(status=SafTicket.PENDING)
    elif filters["status"] == SafTicket.ACCEPTED:
        tickets = tickets.filter(status=SafTicket.ACCEPTED)
    elif filters["status"] == SafTicket.REJECTED:
        tickets = tickets.filter(status=SafTicket.REJECTED)
    else:
        raise Exception("Status '%s' does not exist for tickets" % filters["status"])

    if filters["search"] != None:
        tickets = tickets.filter(
            Q(carbure_id__icontains=filters["search"])
            | Q(supplier__name__icontains=filters["search"])
            | Q(client__name__icontains=filters["search"])
            | Q(feedstock__name__icontains=filters["search"])
            | Q(biofuel__name__icontains=filters["search"])
            | Q(country_of_origin__name__icontains=filters["search"])
            | Q(agreement_reference__icontains=filters["search"])
            | Q(carbure_production_site__name__icontains=filters["search"])
            | Q(unknown_production_site__icontains=filters["search"])
        )

    return tickets


def sort_tickets(tickets, sort_by, order):
    sortable_columns = {
        "client": "client__name",
        "volume": "volume",
        "period": "assignment_period",
        "feedstock": "feedstock__code",
        "ghg_reduction": "ghg_reduction",
    }

    column = sortable_columns.get(sort_by, "created_at")

    if order == "desc":
        return tickets.order_by("-%s" % column)
    else:
        return tickets.order_by(column)
