import traceback
from core.common import ErrorResponse, SuccessResponse
from django.views.decorators.http import require_GET
from core.decorators import check_user_rights
from elec.models.elec_transfer_certificate import ElecTransferCertificate


class ElecSnapshotError:
    YEAR_FAILED = "YEAR_FAILED"


@require_GET
@check_user_rights()
def get_years(request, *args, **kwargs):
    try:
        entity_id = request.GET.get("entity_id")

        transfer_years = (
            ElecTransferCertificate.objects.filter(client_id=entity_id)
            .values_list("transfer_date__year", flat=True)
            .distinct()
        )

        years = list(transfer_years)

        return SuccessResponse(years)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, ElecSnapshotError.YEAR_FAILED)
