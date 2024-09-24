from datetime import datetime
from math import floor

from django import forms
from django.core.paginator import Paginator
from django.db.models import DateField, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from django.views.decorators.http import require_GET

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import Entity
from core.utils import MultipleValueField
from elec.models import ElecChargePoint, ElecMeterReading
from elec.serializers.elec_charge_point import ElecChargePointSerializer
from elec.serializers.elec_charge_point_application import ElecChargePointApplication
from elec.services.export_charge_point_excel import export_charge_points_to_excel


class ChargePointFilterForm(forms.Form):
    status = forms.CharField(required=False)
    application_date = forms.DateField(required=False)
    charge_point_id = MultipleValueField(coerce=str, required=False)
    station_id = MultipleValueField(coerce=str, required=False)
    latest_meter_reading_month = MultipleValueField(required=False)
    is_article_2 = MultipleValueField(required=False)
    search = forms.CharField(required=False)


class ChargePointSortForm(forms.Form):
    from_idx = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


def annotate_with_latest_meter_reading_date(queryset):
    latest_meter_reading_date = (
        ElecMeterReading.objects.filter(meter__charge_point=OuterRef("pk"))
        .order_by("-reading_date")
        .values("reading_date")[:1]
    )
    return queryset.annotate(
        latest_meter_reading_date=Coalesce(Subquery(latest_meter_reading_date), Value(None), output_field=DateField())
    )


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_charge_points(request, entity):
    charge_points_filter_form = ChargePointFilterForm(request.GET)
    charge_points_sort_form = ChargePointSortForm(request.GET)
    selection = request.GET.getlist("selection", [])

    if not charge_points_filter_form.is_valid() or not charge_points_sort_form.is_valid():
        return ErrorResponse(
            400,
            CarbureError.MALFORMED_PARAMS,
            {**charge_points_filter_form.errors, **charge_points_sort_form.errors},
        )

    from_idx = charge_points_sort_form.cleaned_data["from_idx"] or 0
    limit = charge_points_sort_form.cleaned_data["limit"] or 25

    charge_points = ElecChargePoint.objects.filter(cpo=entity, is_deleted=False)
    charge_points = charge_points.select_related("application")
    if selection:
        charge_points = charge_points.filter(id__in=selection)
    charge_points = annotate_with_latest_meter_reading_date(charge_points)
    charge_points = filter_charge_points(charge_points, **charge_points_filter_form.cleaned_data)

    if charge_points_sort_form.cleaned_data["from_idx"] is not None:
        paginator = Paginator(charge_points, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)
        object_list = page.object_list
    else:
        object_list = charge_points

    if "export" in request.GET:
        excel_file = export_charge_points_to_excel(object_list, entity)
        return ExcelResponse(excel_file)

    ids = charge_points.values_list("id", flat=True)
    serialized = ElecChargePointSerializer(object_list, many=True)

    return SuccessResponse(
        {
            "elec_charge_points": serialized.data,
            "ids": list(ids),
            "from": from_idx,
            "returned": len(serialized.data),
            "total": len(ids),
        }
    )


def filter_charge_points(charge_points, **filters):
    charge_points = charge_points.prefetch_related("elec_meters")

    if filters["status"]:
        status_mapping = {
            "PENDING": [ElecChargePointApplication.PENDING],
            "AUDIT_IN_PROGRESS": [ElecChargePointApplication.AUDIT_IN_PROGRESS],
            "ACCEPTED": [ElecChargePointApplication.ACCEPTED],
        }
        charge_points = charge_points.filter(application__status__in=status_mapping[filters["status"]])

    if filters["application_date"]:
        charge_points = charge_points.filter(application__created_at=filters["application_date"])

    if filters["charge_point_id"]:
        charge_points = charge_points.filter(charge_point_id__in=filters["charge_point_id"])

    if filters["station_id"]:
        charge_points = charge_points.filter(station_id__in=filters["station_id"])

    if filters["latest_meter_reading_month"]:
        dates = filters["latest_meter_reading_month"]
        date_filter = Q()
        for date in dates:
            if date == "null":
                date_filter |= Q(latest_meter_reading_date=None)
            else:
                date_obj = datetime.strptime(date, "%m/%Y")
                month = date_obj.month
                year = date_obj.year
                date_filter |= Q(latest_meter_reading_date__month=month, latest_meter_reading_date__year=year)
        charge_points = charge_points.filter(date_filter)

    if filters["is_article_2"]:
        charge_points = charge_points.filter(is_article_2__in=[item == "true" for item in filters["is_article_2"]])

    if filters["search"]:
        search = filters["search"]
        charge_points = charge_points.filter(Q(charge_point_id__icontains=search) | Q(station_id__icontains=search))

    return charge_points
