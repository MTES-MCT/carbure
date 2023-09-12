# /api/v5/elec/provision-certificate/snapshot

import traceback

from django import forms
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from elec.models import ElecTransferCertificate


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
        transfer_certificates = ElecTransferCertificate.objects.filter(transfer_date__year=year, client_id=entity_id)
        return SuccessResponse(
            {
                "transfer_cert_pending": transfer_certificates.filter(status=ElecTransferCertificate.PENDING).count(),
                "transfer_cert_accepted": transfer_certificates.filter(status=ElecTransferCertificate.ACCEPTED).count(),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecOperatorSnapshotError.SNAPSHOT_FAILED)
