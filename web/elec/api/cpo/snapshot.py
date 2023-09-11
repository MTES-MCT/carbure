# /api/v5/elec/provision-certificate/snapshot

import traceback

from django import forms
from django.views.decorators.http import require_GET
from django.db.models import Sum
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from elec.models import ElecProvisionCertificate
from elec.models.elec_transfer_certificate import ElecTransferCertificate


class ElecSnapshotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SNAPSHOT_FAILED = "SNAPSHOT_FAILED"


class ElecSnapshotForm(forms.Form):
    entity_id = forms.IntegerField()
    year = forms.IntegerField()


@require_GET
@check_user_rights()
def get_snapshot(request, *args, **kwargs):
    snapshot_form = ElecSnapshotForm(request.GET)

    if not snapshot_form.is_valid():
        return ErrorResponse(400, ElecSnapshotError.MALFORMED_PARAMS, snapshot_form.errors)

    entity_id = snapshot_form.cleaned_data["entity_id"]
    year = snapshot_form.cleaned_data["year"]
    print('year: ', year)

    try:
        provision_certificates = ElecProvisionCertificate.objects.filter(year=year, cpo_id=entity_id)
        # transfer_certificates = ElecTransferCertificate.objects.filter(year=year, supplier_id=entity_id)

        return SuccessResponse(
            {
                "provisioned_energy": provision_certificates.aggregate(Sum("energy_amount"))["energy_amount__sum"] or 0,  # fmt:skip
                "remaining_energy": provision_certificates.aggregate(Sum("remaining_energy_amount"))["remaining_energy_amount__sum"] or 0,  # fmt:skip
                "provision_cert_available": provision_certificates.filter(remaining_energy_amount__gt=0).count(),
                "provision_cert_history": provision_certificates.filter(remaining_energy_amount=0).count(),
                # "transferred_energy": transfer_certificates.aggregate(Sum("energy_amount"))["energy_amount__sum"] or 0,  # fmt:skip
                # "transfer_certificates_pending": transfer_certificates.filter(status=ElecTransferCertificate.PENDING).count(),
                # "transfer_certificates_accepted": transfer_certificates.filter(status=ElecTransferCertificate.ACCEPTED).count(),
                # "transfer_certificates_rejected": transfer_certificates.filter(status=ElecTransferCertificate.REJECTED).count(),
                "transferred_energy": 0,
                "transfer_certificates_pending": 0,
                "transfer_certificates_accepted": 0,
                "transfer_certificates_rejected": 0,
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecSnapshotError.SNAPSHOT_FAILED)
