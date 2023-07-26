import traceback
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.models.elec_transfer_certificate import ElecTransferCertificate


class ElecSnapshotError:
    YEAR_FAILED = "YEAR_FAILED"


@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def get_years(request):
    try:
        provision_years = ElecProvisionCertificate.objects.values_list("year", flat=True).distinct()
        transfer_years = ElecTransferCertificate.objects.values_list("transfer_date__year", flat=True).distinct()

        years = list(set(list(provision_years) + list(transfer_years)))

        return SuccessResponse({"years": years})
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecSnapshotError.YEAR_FAILED)
