import traceback

from django import forms
from django.views.decorators.http import require_GET

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from elec.serializers.elec_transfer_certificate import ElecTransferCertificateDetailsSerializer


class TransferCertificatesError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    TRANSFER_CERTIFICATE_LOADING_FAILED = "TRANSFER_CERTIFICATE_LOADING_FAILED"


class TransferCertificateDetailsForm(forms.Form):
    transfer_certificate_id = forms.IntegerField()


@require_GET
@check_user_rights()
def get_transfer_certificate_details(request, *args, **kwargs):
    transf_certif_form = TransferCertificateDetailsForm(request.GET)

    if not transf_certif_form.is_valid():
        return ErrorResponse(400, TransferCertificatesError.MALFORMED_PARAMS, transf_certif_form.errors)

    transfer_certificate_id = transf_certif_form.cleaned_data["transfer_certificate_id"]

    try:
        transfer_certificates = ElecTransferCertificate.objects.get(id=transfer_certificate_id)
        serialized = ElecTransferCertificateDetailsSerializer(transfer_certificates)

        return SuccessResponse(
            {
                "elec_transfer_certificate": serialized.data,
            }
        )

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, TransferCertificatesError.TRANSFER_CERTIFICATE_LOADING_FAILED)
