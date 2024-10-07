from math import floor

from django import forms
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.serializers.elec_charge_point_application import ElecChargePointApplication, ElecChargePointApplicationSerializer


class ApplicationsFilterForm(forms.Form):
    year = forms.IntegerField(required=False)
    status = forms.CharField(required=False)


class ApplicationsSortForm(forms.Form):
    from_idx = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


@require_GET
@check_user_rights(entity_type=[Entity.CPO])
def get_applications(request, entity):
    applications_filter_form = ApplicationsFilterForm(request.GET)
    applications_sort_form = ApplicationsSortForm(request.GET)

    if not applications_filter_form.is_valid() or not applications_sort_form.is_valid():
        return ErrorResponse(
            400,
            CarbureError.MALFORMED_PARAMS,
            {**applications_filter_form.errors, **applications_sort_form.errors},
        )

    from_idx = applications_sort_form.cleaned_data["from_idx"] or 0
    limit = applications_sort_form.cleaned_data["limit"] or 25

    applications = ChargePointRepository.get_annotated_applications_by_cpo(entity)
    applications = filter_charge_point_applications(applications, **applications_filter_form.cleaned_data)

    if applications_sort_form.cleaned_data["from_idx"] is not None:
        paginator = Paginator(applications, limit)
        current_page = floor(from_idx / limit) + 1
        page = paginator.page(current_page)
        object_list = page.object_list
    else:
        object_list = applications
    serialized = ElecChargePointApplicationSerializer(object_list, many=True).data
    return SuccessResponse(serialized)


def filter_charge_point_applications(applications, **filters):
    if filters["year"]:
        applications = applications.filter(created_at__year=filters["year"])

    if filters["status"]:
        status_mapping = {
            "PENDING": [ElecChargePointApplication.PENDING],
            "AUDIT_IN_PROGRESS": [ElecChargePointApplication.AUDIT_IN_PROGRESS],
            "AUDIT_DONE": [ElecChargePointApplication.AUDIT_DONE],
            "HISTORY": [ElecChargePointApplication.REJECTED, ElecChargePointApplication.ACCEPTED],
        }
        applications = applications.filter(status__in=status_mapping[filters["status"]])
    return applications
