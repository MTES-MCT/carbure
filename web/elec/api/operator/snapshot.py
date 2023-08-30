# /api/v5/elec/provision-certificate/snapshot

import traceback

from django import forms
from django.db.models import Sum
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from elec.models import ElecProvisionCertificate


class ElecOperatorSnapshotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SNAPSHOT_FAILED = "SNAPSHOT_FAILED"


class ElecSnapshotForm(forms.Form):
    entity_id = forms.IntegerField()
    year = forms.IntegerField()


@check_user_rights()
def get_snapshot(request, *args, **kwargs):
    snapshot_form = ElecSnapshotForm(request.GET)

    if not snapshot_form.is_valid():
        return ErrorResponse(400, ElecOperatorSnapshotError.MALFORMED_PARAMS, snapshot_form.errors)

    entity_id = snapshot_form.cleaned_data["entity_id"]
    year = snapshot_form.cleaned_data["year"]

    try:
        provision_certificates = ElecProvisionCertificate.objects.filter(year=year, entity_id=entity_id)
        return SuccessResponse(
            {
                "provision_cert_available": provision_certificates.filter(remaining_energy_amount__gt=0).count(),
                "provision_cert_history": provision_certificates.filter(remaining_energy_amount=0).count(),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecOperatorSnapshotError.SNAPSHOT_FAILED)
