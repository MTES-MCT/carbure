import traceback
from django import forms
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.models.elec_transfer_certificate import ElecTransferCertificate


class ElecSnapshotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SNAPSHOT_FAILED = "SNAPSHOT_FAILED"


class ElecSnapshotForm(forms.Form):
    year = forms.IntegerField()


@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_snapshot(request):
    snapshot_form = ElecSnapshotForm(request.GET)

    if not snapshot_form.is_valid():
        return ErrorResponse(400, ElecSnapshotError.MALFORMED_PARAMS, snapshot_form.errors)

    year = snapshot_form.cleaned_data["year"]

    try:
        provision_certificates = ElecProvisionCertificate.objects.filter(year=year)
        transfer_certificates = ElecTransferCertificate.objects.filter(transfer_date__year=year)

        return SuccessResponse(
            {
                "provision_certificates": provision_certificates.count(),
                "transfer_certificates": transfer_certificates.count(),
            }
        )
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecSnapshotError.SNAPSHOT_FAILED)
