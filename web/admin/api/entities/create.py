# /api/v5/saf/operator/assign-ticket

import traceback
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_admin_rights
from core.models import Entity, ExternalAdminRights


class CreateEntityError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    ENTITY_EXISTS = "ENTITY_EXISTS"
    ENTITY_CREATION_FAILED = "ENTITY_CREATION_FAILED"


@check_admin_rights(allow_external=[ExternalAdminRights.AIRLINE])
def create_entity(request, *args, **kwargs):
    try:
        name = request.POST.get("name")
        entity_type = request.POST.get("entity_type")
        has_saf = request.POST.get("has_saf") == "true"
    except:
        traceback.print_exc()
        return ErrorResponse(400, CreateEntityError.MALFORMED_PARAMS)

    entities = Entity.objects.filter(name=name)
    if entities.count() > 0:
        return ErrorResponse(400, CreateEntityError.ENTITY_EXISTS)

    try:
        Entity.objects.create(name=name, entity_type=entity_type, has_saf=has_saf)

        return SuccessResponse()
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CreateEntityError.ENTITY_CREATION_FAILED)
