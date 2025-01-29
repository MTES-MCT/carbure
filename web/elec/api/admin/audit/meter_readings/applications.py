import traceback
from math import floor

from django import forms
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from core.utils import MultipleValueField
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.repositories.meter_reading_repository import MeterReadingRepository
from elec.serializers.elec_meter_reading_application import ElecMeterReadingApplicationSerializer


class AuditApplicationsSortForm(forms.Form):
    from_idx = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


class AuditApplicationsFilterForm(forms.Form):
    year = forms.IntegerField()
    status = forms.CharField()
    cpo = MultipleValueField(coerce=str, required=False)
    quarter = MultipleValueField(coerce=str, required=False)


@require_GET
@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_applications(request):
    audit_applications_filter_form = AuditApplicationsFilterForm(request.GET)
    audit_applications_sort_form = AuditApplicationsSortForm(request.GET)

    if not audit_applications_filter_form.is_valid() or not audit_applications_sort_form.is_valid():
        return ErrorResponse(
            400,
            CarbureError.MALFORMED_PARAMS,
            {**audit_applications_filter_form.errors, **audit_applications_sort_form.errors},
        )

    from_idx = audit_applications_sort_form.cleaned_data["from_idx"] or 0
    limit = audit_applications_sort_form.cleaned_data["limit"] or 25

    try:
        meter_readings_applications = MeterReadingRepository.get_annotated_applications()
        meter_readings_applications = filter_meter_readings_applications(
            meter_readings_applications, **audit_applications_filter_form.cleaned_data
        )

        paginator = Paginator(meter_readings_applications, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)

        ids = meter_readings_applications.values_list("id", flat=True)

        serialized = ElecMeterReadingApplicationSerializer(page.object_list, many=True)

        return SuccessResponse(
            {
                "meter_readings_applications": serialized.data,
                "ids": list(ids),
                "from": from_idx,
                "returned": len(serialized.data),
                "total": len(ids),
            }
        )

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)


def filter_meter_readings_applications(applications, **filters):
    applications = applications.select_related("cpo")
    applications = applications.filter(year=filters["year"])

    if filters.get("cpo"):
        applications = applications.filter(cpo__name__in=filters["cpo"])

    if filters.get("quarter"):
        applications = applications.filter(quarter__in=filters["quarter"])

    if filters.get("status") == "PENDING":
        applications = applications.filter(status=ElecMeterReadingApplication.PENDING)
    elif filters.get("status") == "AUDIT_IN_PROGRESS":
        applications = applications.filter(status=ElecMeterReadingApplication.AUDIT_IN_PROGRESS)
    elif filters.get("status") == "AUDIT_DONE":
        applications = applications.filter(status=ElecMeterReadingApplication.AUDIT_DONE)
    elif filters.get("status") == "HISTORY":
        applications = applications.filter(
            status__in=[ElecMeterReadingApplication.REJECTED, ElecMeterReadingApplication.ACCEPTED]
        )

    return applications
