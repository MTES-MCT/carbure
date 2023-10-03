from math import floor
import traceback
from django import forms

from django.views.decorators.http import require_GET
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.serializers.elec_provision_certificate import ElecProvisionCertificateSerializer


class ProvisionCertificatesError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    PROVISION_CERTIFICATE_LOADING_FAILED = "PROVISION_CERTIFICATE_LOADING_FAILED"


class ProvisionCertificateDetailsForm(forms.Form):
    provision_certificate_id = forms.IntegerField()


@require_GET
@check_user_rights()
def get_provision_certificate_details(request):
    provision_certif_form = ProvisionCertificateDetailsForm(request.GET)

    if not provision_certif_form.is_valid():
        return ErrorResponse(400, ProvisionCertificatesError.MALFORMED_PARAMS, provision_certif_form.errors)

    entity_id = request.GET.get("entity_id")
    provision_certificate_id = provision_certif_form.cleaned_data["provision_certificate_id"]

    try:
        provision_certificate = ElecProvisionCertificate.objects.get(id=provision_certificate_id, cpo_id=entity_id)
        serialized = ElecProvisionCertificateSerializer(provision_certificate)

        return SuccessResponse(
            {
                "elec_Provision_certificate": serialized.data,
            }
        )

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ProvisionCertificatesError.Provision_CERTIFICATE_LOADING_FAILED)
