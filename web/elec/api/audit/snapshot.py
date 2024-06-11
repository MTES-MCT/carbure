from django import forms
from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.models.elec_audit_sample import ElecAuditSample
from elec.repositories.elec_audit_repository import ElecAuditRepository


class ElecAuditSnapshotForm(forms.Form):
    year = forms.IntegerField()


@check_user_rights(entity_type=[Entity.AUDITOR])
def get_snapshot(request):
    snapshot_form = ElecAuditSnapshotForm(request.GET)

    if not snapshot_form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, snapshot_form.errors)

    year = snapshot_form.cleaned_data["year"]

    audits = ElecAuditRepository.get_audited_applications(request.user).filter(created_at__year=year)

    return SuccessResponse(
        {
            "charge_points_applications_audit_done": audits.filter(status=ElecAuditSample.AUDITED).count(),
            "charge_points_applications_audit_in_progress": audits.filter(status=ElecAuditSample.IN_PROGRESS).count(),
        }
    )
