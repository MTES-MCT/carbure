from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationDetailsSerializer
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from doublecount.api.admin.applications.export_application import check_has_dechets_industriels
from doublecount.helpers import get_agreement_quotas


class DoubleCountingAgreementError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"


@check_admin_rights(allow_external=[ExternalAdminRights.DOUBLE_COUNTING])
def get_agreement_details(request, *args, **kwargs):
    agreement_id = request.GET.get("agreement_id", None)

    if not agreement_id:
        return ErrorResponse(400, DoubleCountingAgreementError.MALFORMED_PARAMS)

    agreement = DoubleCountingRegistration.objects.get(id=agreement_id)

    # return JsonResponse(
    #     {"status": "success", "data": DoubleCountingRegistrationDetailsSerializer(agreement, many=False).data}
    # )

    result = DoubleCountingRegistrationDetailsSerializer(agreement, many=False).data
    result["quotas"] = get_agreement_quotas(agreement)
    result["has_dechets_industriels"] = False
    if agreement.application:
        result["has_dechets_industriels"] = check_has_dechets_industriels(agreement.application)

    return SuccessResponse(result)
