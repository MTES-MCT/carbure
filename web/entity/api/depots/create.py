from django.views.decorators.http import require_POST
from core.models import UserRights
from core.decorators import check_rights
from core.serializers import DepotSerializer
from core.common import ErrorResponse, SuccessResponse
from core.carburetypes import CarbureError


@require_POST
@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def create_depot(request, context):
    serializer = DepotSerializer(data=request.POST)

    if not serializer.is_valid():
        errors = {key: e for key, e in serializer.errors.items()}
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, data=errors)

    print("country", serializer.validated_data)

    serializer.save()

    return SuccessResponse()
