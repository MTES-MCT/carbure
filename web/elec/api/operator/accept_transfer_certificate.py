# /api/v5/elec/provision-certificate/snapshot

import traceback
import datetime

from django import forms
from django.db.models import Sum, F
from django.db import transaction
from django.views.decorators.http import require_POST
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from core.models import CarbureNotification, Entity, UserRights
from elec.models import ElecProvisionCertificate, ElecTransferCertificate

from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer


class ElecRejectError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    ACCEPT_FAILED = "ACCEPT_FAILED"


class ElecTransferForm(forms.Form):
    entity_id = forms.IntegerField()
    transfer_certificate_id = forms.ModelChoiceField(queryset=ElecTransferCertificate.objects.all(), required=False)


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def accept_transfer_certificate(request, *args, **kwargs):
    transfer_form = ElecTransferForm(request.POST)

    if not transfer_form.is_valid():
        return ErrorResponse(400, ElecRejectError.MALFORMED_PARAMS, transfer_form.errors)

    transfer_certificate = transfer_form.cleaned_data["transfer_certificate_id"]

    try:
        transfer_certificate.status = ElecTransferCertificate.ACCEPTED
        transfer_certificate.save()
        return SuccessResponse()
    except:
        traceback.print_exc()
        return ErrorResponse(400, ElecRejectError.ACCEPT_FAILED)

    # TODO: Create verification function to preserve integrity of the certificates
