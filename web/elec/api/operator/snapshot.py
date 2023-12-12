# /api/elec/provision-certificate/snapshot

import traceback

from django import forms
from django.db.models import Sum
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
        accepted_transfer_certificates = transfer_certificates.filter(status=ElecTransferCertificate.ACCEPTED)

        return SuccessResponse(
            {
                "transfer_cert_pending": transfer_certificates.filter(status=ElecTransferCertificate.PENDING).count(),
                "transfer_cert_accepted": accepted_transfer_certificates.count(),
                "acquired_energy": accepted_transfer_certificates.aggregate(Sum("energy_amount"))["energy_amount__sum"] or 0,
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecOperatorSnapshotError.SNAPSHOT_FAILED)
