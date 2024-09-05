from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity
from elec.serializers.elec_charge_point import ElecChargePointUpdateSerializer


class ChargePointDeleteError:
    CP_NOT_FOUND_ON_CPO = "CP_NOT_FOUND_ON_CPO"


@check_user_rights(entity_type=[Entity.CPO])
def delete_charge_point(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]

    serializer = ElecChargePointUpdateSerializer(data=request.POST, partial=True)
    if not serializer.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, serializer.errors)

    cp = serializer.validated_data["id"]
    entity = Entity.objects.get(id=entity_id)
    if cp.cpo != entity:
        return ErrorResponse(400, ChargePointDeleteError.CP_NOT_FOUND_ON_CPO)

    cp.is_deleted = True
    cp.save(update_fields=["is_deleted"])

    return SuccessResponse()
