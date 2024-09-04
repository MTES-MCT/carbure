from math import floor

from django import forms
from django.core.paginator import Paginator
from django.db.models import FloatField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.views.decorators.http import require_GET

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.excel import ExcelResponse
from core.models import Entity
from elec.models import ElecChargePoint, ElecMeterReading
from elec.serializers.elec_charge_point import ElecChargePointSerializer
from elec.serializers.elec_charge_point_application import ElecChargePointApplication
from elec.services.export_charge_point_excel import export_charge_points_to_excel


class ChargePointFilterForm(forms.Form):
    year = forms.IntegerField(required=False)
    status = forms.CharField(required=False)
    application_date = forms.DateField(required=False)
    charge_point_id = forms.CharField(required=False)
    latest_extracted_energy = forms.FloatField(required=False)
    is_article_2 = forms.BooleanField(required=False)


class ChargePointSortForm(forms.Form):
    from_idx = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


def annotate_with_latest_extracted_energy(queryset):
    latest_extracted_energy_subquery = (
        ElecMeterReading.objects.filter(meter__charge_point=OuterRef("pk"))
        .order_by("-reading_date")
        .values("extracted_energy")[:1]
    )
    return queryset.annotate(
        latest_extracted_energy=Coalesce(Subquery(latest_extracted_energy_subquery), Value(0), output_field=FloatField())
    )


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

    charge_points = ElecChargePoint.objects.filter(cpo=entity, is_deleted=False)
    charge_points = charge_points.select_related("application")
    charge_points = annotate_with_latest_extracted_energy(charge_points)
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
            "charge_points_list": serialized.data,
            "ids": list(ids),
            "from": from_idx,
            "returned": len(serialized.data),
            "total": len(ids),
        }
    )


def filter_charge_points(charge_points, **filters):
    charge_points = charge_points.prefetch_related("elec_meters")

    if filters["year"]:
        charge_points = charge_points.filter(application__created_at__year=filters["year"])

    if filters["status"]:
        status_mapping = {
            "PENDING": [ElecChargePointApplication.PENDING],
            "AUDIT_IN_PROGRESS": [ElecChargePointApplication.AUDIT_IN_PROGRESS],
            "AUDIT_DONE": [ElecChargePointApplication.AUDIT_DONE],
            "ACCEPTED": [ElecChargePointApplication.ACCEPTED],
        }
        charge_points = charge_points.filter(application__status__in=status_mapping[filters["status"]])

    if filters["application_date"]:
        charge_points = charge_points.filter(application__created_at=filters["application_date"])

    if filters["charge_point_id"]:
        charge_points = charge_points.filter(charge_point_id=filters["charge_point_id"])

    if filters["latest_extracted_energy"] is not None:
        charge_points = charge_points.filter(latest_extracted_energy=filters["latest_extracted_energy"])

    if filters["is_article_2"]:
        charge_points = charge_points.filter(is_article_2=filters["is_article_2"])

    return charge_points
