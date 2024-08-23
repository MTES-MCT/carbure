# /api/elec/provision-certificate/snapshot

import traceback

from django import forms
from django.views.decorators.http import require_POST

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import UserRights
from elec.models import ElecTransferCertificate


class ElecRejectError:
    ALREADY_ACCEPTED = "ALREADY_ACCEPTED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    REJECT_FAILED = "REJECT_FAILED"


class ElecTransferForm(forms.Form):
    entity_id = forms.IntegerField()
    transfer_certificate_id = forms.ModelChoiceField(queryset=ElecTransferCertificate.objects.all(), required=False)
    comment = forms.CharField()


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def reject_transfer_certificate(request, *args, **kwargs):
    transfer_form = ElecTransferForm(request.POST)

    if not transfer_form.is_valid():
        return ErrorResponse(400, ElecRejectError.MALFORMED_PARAMS, transfer_form.errors)

    transfer_certificate = transfer_form.cleaned_data["transfer_certificate_id"]
    comment = transfer_form.cleaned_data["comment"]

    if transfer_certificate.status == ElecTransferCertificate.ACCEPTED:
        return ErrorResponse(400, ElecRejectError.ALREADY_ACCEPTED)

    try:
        transfer_certificate.status = ElecTransferCertificate.REJECTED
        transfer_certificate.comment = comment
        transfer_certificate.save()
        return SuccessResponse()
    except:
        traceback.print_exc()
        return ErrorResponse(400, ElecRejectError.REJECT_FAILED)

    # TODO: Create verification function to preserve integrity of the certificates
