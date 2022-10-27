# /api/v5/saf/tickets

from math import floor
import traceback
from django.core.paginator import Paginator
from core.common import SuccessResponse, ErrorResponse
from core.models import Entity
from django.contrib.auth.decorators import login_required
from saf.serializers.saf_ticket import SafClientSerializer


class SafClientsError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    CLIENT_LISTING_FAILED = "CLIENT_LISTING_FAILED"


@login_required
def get_clients(request, *args, **kwargs):
    try:
        q = request.GET.get('query', False)
        # TODO Entity.AIRLINE
        entities = Entity.objects.filter(entity_type=Entity.AIRLINE).order_by('name')
    except:
        traceback.print_exc()
        return ErrorResponse(400, SafClientsError.MALFORMED_PARAMS)

    if q:
        entities = entities.filter(name__icontains=q)

    try:
        serialized = SafClientSerializer(entities, many=True)
        return SuccessResponse(serialized.data)
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, SafClientsError.CLIENT_LISTING_FAILED)
