# /api/saf/operator/clients

import traceback

from django.contrib.auth.decorators import login_required
from django.db.models import Q

from core.common import ErrorResponse, SuccessResponse
from core.models import Entity
from saf.serializers.saf_ticket import SafClientSerializer


class SafClientsError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    CLIENT_LISTING_FAILED = "CLIENT_LISTING_FAILED"


@login_required
def get_clients(request, *args, **kwargs):
    try:
        entity_id = request.GET.get("entity_id", False)
        q = request.GET.get("query", False)
        is_airline = Q(entity_type=Entity.AIRLINE)
        is_saf_operator = Q(entity_type=Entity.OPERATOR, has_saf=True)
        entities = Entity.objects.filter(is_airline | is_saf_operator).order_by("name")

    except:
        traceback.print_exc()
        return ErrorResponse(400, SafClientsError.MALFORMED_PARAMS)

    if entity_id:
        entities = entities.exclude(id=entity_id)

    if q:
        entities = entities.filter(name__icontains=q)

    try:
        serialized = SafClientSerializer(entities, many=True)
        return SuccessResponse(serialized.data)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafClientsError.CLIENT_LISTING_FAILED)
