from certificates.models import DoubleCountingRegistration
from core.decorators import check_admin_rights

from doublecount.models import (
    DoubleCountingApplication,
    DoubleCountingProduction,
)
from doublecount.helpers import (
    send_dca_status_email,
)

from core.common import ErrorResponse, SuccessResponse


class DoubleCountingApplicationApproveError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"
    QUOTAS_NOT_APPROVED = "QUOTAS_NOT_APPROVED"


@check_admin_rights()
def approve_dca(request, *args, **kwargs):
    dca_id = request.POST.get("dca_id", False)
    if not dca_id:
        return ErrorResponse(400, DoubleCountingApplicationApproveError.MALFORMED_PARAMS)

    try:
        application = DoubleCountingApplication.objects.get(id=dca_id)
    except:
        return ErrorResponse(400, DoubleCountingApplicationApproveError.APPLICATION_NOT_FOUND)

    # ensure all quotas have been validated
    remaining_quotas_to_check = DoubleCountingProduction.objects.filter(dca=application, approved_quota=-1).count()
    if remaining_quotas_to_check > 0:
        return ErrorResponse(400, DoubleCountingApplicationApproveError.QUOTAS_NOT_APPROVED)

    application.status = DoubleCountingApplication.ACCEPTED
    application.save()  # save before sending email, just in case

    # create Agreement

    production_site_address = (
        application.production_site.address
        + " "
        + application.production_site.city
        + " "
        + application.production_site.postal_code
        + " "
        + application.production_site.country.name
    )

    if not DoubleCountingRegistration.objects.filter(certificate_id=application.agreement_id).exists():
        try:
            DoubleCountingRegistration.objects.update_or_create(
                certificate_id=application.agreement_id,
                certificate_holder=application.producer.name, #TO DELETE replaced by production_site.producer.name
                production_site=application.production_site,
                registered_address=production_site_address, #TO DELETE replaced by production_site.address
                valid_from=application.period_start,
                valid_until=application.period_end,
                application=application,
            )
        except:
            return ErrorResponse(400, "Error while creating Agreement")

    # send_dca_status_email(application) TODO: uncomment when email is ready
    return SuccessResponse()
