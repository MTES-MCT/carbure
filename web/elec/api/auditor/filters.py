from core.carburetypes import CarbureError
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.api.admin.audit.charge_points.applications import AuditApplicationsFilterForm
from elec.repositories.elec_audit_repository import ElecAuditRepository


@check_user_rights(entity_type=[Entity.AUDITOR])
def get_application_filters(request):
    filter_form = AuditApplicationsFilterForm(request.GET)

    if not filter_form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, filter_form.errors)

    filter = request.GET.get("filter")

    # do not apply the filter we are listing so we can get all its possible values in the current context
    query = filter_form.cleaned_data
    query[filter] = None

    applications = ElecAuditRepository.get_audited_applications(request.user, **query)

    if filter == "cpo":
        values = list(applications.values_list("cpo__name", flat=True).distinct())
    else:
        values = []

    return SuccessResponse(values)
