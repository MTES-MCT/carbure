from math import floor
import traceback
from django import forms

from django.core.paginator import Paginator
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.serializers.elec_provision_certificate import ElecProvisionCertificateSerializer


class ProvisionCertificatesError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    PROVISION_CERTIFICATES_LISTING_FAILED = "PROVISION_CERTIFICATES_LISTING_FAILED"


class ProvisionCertificateDetailsForm(forms.Form):
    provision_certificate_id = forms.IntegerField()


@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_provision_certificate_details(request):
    provision_certif_form = ProvisionCertificateDetailsForm(request.GET)

    if not provision_certif_form.is_valid():
        return ErrorResponse(400, ProvisionCertificatesError.MALFORMED_PARAMS, provision_certif_form.errors)

    provision_certificate_id = provision_certif_form.cleaned_data["provision_certificate_id"]

    try:
        provision_certificates = ElecProvisionCertificate.objects.get(id=provision_certificate_id)
        serialized = ElecProvisionCertificateSerializer(provision_certificates)

        return SuccessResponse(
            {
                "elec_Provision_certificate": serialized.data,
            }
        )

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ProvisionCertificatesError.Provision_CERTIFICATES_LISTING_FAILED)
