from django.db.models import OuterRef, Subquery, F
from django.views.decorators.http import require_GET
from django import forms
from django.core.paginator import Paginator
from math import floor
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import Entity
from elec.models import ElecChargePoint, ElecMeterReading
from elec.serializers.elec_charge_point import ElecChargePointSerializer
from elec.services.export_charge_point_excel import export_charge_points_to_excel
from elec.serializers.elec_charge_point_application import ElecChargePointApplication
from core.carburetypes import CarbureError


class ChargePointFilterForm(forms.Form):
    year = forms.IntegerField(required=False)
    status = forms.CharField(required=False)
    created_at = forms.DateField(required=False)
    charge_point_id = forms.CharField(required=False)
    last_extracted_energy = forms.FloatField(required=False)
    is_article_2 = forms.BooleanField(required=False)


class ChargePointSortForm(forms.Form):
    from_idx = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_charge_points(request, entity):
    charge_points_filter_form = ChargePointFilterForm(request.GET)
    charge_points_sort_form = ChargePointSortForm(request.GET)

    if not charge_points_filter_form.is_valid() or not charge_points_sort_form.is_valid():
        return ErrorResponse(
            400,
            CarbureError.MALFORMED_PARAMS,
            {**charge_points_filter_form.errors, **charge_points_sort_form.errors},
        )

    from_idx = charge_points_sort_form.cleaned_data["from_idx"] or 0
    limit = charge_points_sort_form.cleaned_data["limit"] or 25

    charge_points = ElecChargePoint.objects.filter(cpo=entity)

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

    serialized = ElecChargePointSerializer(object_list, many=True).data
    return SuccessResponse(serialized)


def filter_charge_points(charge_points, **filters):
    charge_points = charge_points.prefetch_related("elec_meters")

    if filters["year"]:
        charge_points = charge_points.filter(application__created_at__year=filters["year"])

    if filters["status"]:
        status_mapping = {
            "PENDING": [ElecChargePointApplication.PENDING],
            "AUDIT_IN_PROGRESS": [ElecChargePointApplication.AUDIT_IN_PROGRESS],
            "AUDIT_DONE": [ElecChargePointApplication.AUDIT_DONE],
            "HISTORY": [ElecChargePointApplication.REJECTED, ElecChargePointApplication.ACCEPTED],
        }
        charge_points = charge_points.filter(application__status__in=status_mapping[filters["status"]])

    if filters["created_at"]:
        charge_points = charge_points.filter(application__created_at=filters["created_at"])

    if filters["charge_point_id"]:
        charge_points = charge_points.filter(charge_point_id=filters["charge_point_id"])

    if filters["last_extracted_energy"] is not None:
        latest_reading_subquery = (
            ElecMeterReading.objects.filter(meter__charge_point=OuterRef("pk")).order_by("-reading_date").values("pk")[:1]
        )
        charge_points = charge_points.annotate(latest_reading_id=Subquery(latest_reading_subquery))
        charge_points = charge_points.filter(
            current_meter__elec_meter_readings__pk=F("latest_reading_id"),
            current_meter__elec_meter_readings__extracted_energy=filters["last_extracted_energy"],
        )
        charge_points = charge_points.filter(current_meter__elec_meter_readings__extracted_energy=filters["last_extracted_energy"])

    if filters["is_article_2"]:
        charge_points = charge_points.filter(is_article_2=filters["is_article_2"])

    return charge_points
