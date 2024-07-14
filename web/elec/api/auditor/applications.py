from math import floor
from django import forms
from django.views.decorators.http import require_GET
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from core.utils import MultipleValueField
from elec.repositories.elec_audit_repository import ElecAuditRepository
from elec.serializers.elec_audit_sample_serializer import ElecAuditSampleSerializer
from django.core.paginator import Paginator


class AuditApplicationsSortForm(forms.Form):
    from_idx = forms.IntegerField(required=False)
    limit = forms.IntegerField(required=False)


class AuditApplicationsFilterForm(forms.Form):
    year = forms.IntegerField()
    status = forms.CharField()
    cpo = MultipleValueField(coerce=str, required=False)


@require_GET
@check_user_rights(entity_type=[Entity.AUDITOR])
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

    applications = ElecAuditRepository.get_audited_applications(request.user, **audit_applications_filter_form.cleaned_data)

    paginator = Paginator(applications, limit)
    current_page = floor(from_idx / limit) + 1
    page = paginator.page(current_page)

    ids = applications.values_list("id", flat=True)
    serialized = ElecAuditSampleSerializer(page.object_list, many=True)

    return SuccessResponse(
        {
            "audit_applications": serialized.data,
            "ids": list(ids),
            "from": from_idx,
            "returned": len(serialized.data),
            "total": len(ids),
        }
    )
