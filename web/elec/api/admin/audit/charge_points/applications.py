from math import floor
import traceback
from django import forms
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from core.utils import MultipleValueField
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point_application import ElecChargePointApplicationSerializer
from django.core.paginator import Paginator
from django.db.models import Count, Sum


class AuditApplicationsSortForm(forms.Form):
    from_idx = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


class AuditApplicationsFilterForm(forms.Form):
    year = forms.IntegerField()
    status = forms.CharField()
    cpo = MultipleValueField(coerce=str, required=False)


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
        charge_points_applications = ChargePointRepository.get_annotated_applications()
        charge_points_applications = filter_charge_point_applications(
            charge_points_applications, **audit_applications_filter_form.cleaned_data
        )

        paginator = Paginator(charge_points_applications, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)

        ids = charge_points_applications.values_list("id", flat=True)

        serialized = ElecChargePointApplicationSerializer(page.object_list, many=True)

        return SuccessResponse(
            {
                "charge_points_applications": serialized.data,
                "ids": list(ids),
                "from": from_idx,
                "returned": len(serialized.data),
                "total": len(ids),
            }
        )

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CarbureError.UNKNOWN_ERROR)


def filter_charge_point_applications(applications, **filters):
    applications = applications.select_related(
        "cpo",
    )

    applications = applications.filter(created_at__year=filters["year"])

    if filters["cpo"]:
        applications = applications.filter(cpo__name__in=filters["cpo"])

    if filters["status"] == "PENDING":
        applications = applications.filter(status=ElecChargePointApplication.PENDING)
    elif filters["status"] == "AUDIT_IN_PROGRESS":
        applications = applications.filter(status=ElecChargePointApplication.AUDIT_IN_PROGRESS)
    elif filters["status"] == "AUDIT_DONE":
        applications = applications.filter(status=ElecChargePointApplication.AUDIT_DONE)
    elif filters["status"] == "HISTORY":
        applications = applications.filter(
            status__in=[ElecChargePointApplication.REJECTED, ElecChargePointApplication.ACCEPTED]
        )

    return applications
