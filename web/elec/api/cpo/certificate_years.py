import traceback
from core.common import ErrorResponse, SuccessResponse
from django.views.decorators.http import require_GET
from core.decorators import check_user_rights
from core.models import UserRights
from elec.models.elec_provision_certificate import ElecProvisionCertificate
from elec.models.elec_transfer_certificate import ElecTransferCertificate


class ElecSnapshotError:
    YEAR_FAILED = "YEAR_FAILED"


@require_GET
@check_user_rights()
def get_certificate_years(request, *args, **kwargs):
    try:
        entity_id = request.GET.get("entity_id")

        provision_years = ElecProvisionCertificate.objects.filter(cpo_id=entity_id).values_list("year", flat=True).distinct()

        transfer_years = (
            ElecTransferCertificate.objects.filter(supplier_id=entity_id)
            .values_list("transfer_date__year", flat=True)
            .distinct()
        )

        years = list(set(list(provision_years) + list(transfer_years)))

        return SuccessResponse(years)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecSnapshotError.YEAR_FAILED)
