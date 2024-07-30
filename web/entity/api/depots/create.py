from django.views.decorators.http import require_POST
from core.models import UserRights
from core.decorators import check_rights
from entity.serializers.depot import DepotSerializer
from core.common import ErrorResponse, SuccessResponse
from core.carburetypes import CarbureError


@require_POST
@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def create_depot(request, context):
    data = request.POST.copy()
    data["entity"] = context["entity"].id

    serializer = DepotSerializer(data=data)

    if not serializer.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, data=serializer.errors)

    serializer.save()

    return SuccessResponse()
