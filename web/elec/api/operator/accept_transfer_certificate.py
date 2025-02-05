# /api/elec/provision-certificate/snapshot

import traceback

from django import forms
from django.views.decorators.http import require_POST

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import UserRights
from elec.models import ElecTransferCertificate


class ElecRejectError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    ACCEPT_FAILED = "ACCEPT_FAILED"


class ElecTransferForm(forms.Form):
    entity_id = forms.IntegerField()
    transfer_certificate_id = forms.ModelChoiceField(queryset=ElecTransferCertificate.objects.all(), required=False)
    used_in_tiruert = forms.CharField()
    consumption_date = forms.DateField(required=False)


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def accept_transfer_certificate(request, *args, **kwargs):
    post_data = request.POST.copy()
    post_data["used_in_tiruert"] = "true" if post_data.get("used_in_tiruert", "").lower() == "true" else "false"
    transfer_form = ElecTransferForm(post_data)

    if not transfer_form.is_valid():
        return ErrorResponse(400, ElecRejectError.MALFORMED_PARAMS, transfer_form.errors)

    transfer_certificate = transfer_form.cleaned_data["transfer_certificate_id"]
    used_in_tiruert = transfer_form.cleaned_data["used_in_tiruert"]
    consumption_date = transfer_form.cleaned_data["consumption_date"]

    try:
        transfer_certificate.status = ElecTransferCertificate.ACCEPTED
        transfer_certificate.used_in_tiruert = used_in_tiruert == "true"
        if consumption_date:
            transfer_certificate.consumption_date = consumption_date
        transfer_certificate.save()
        return SuccessResponse()
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecRejectError.ACCEPT_FAILED)

    # TODO: Create verification function to preserve integrity of the certificates
