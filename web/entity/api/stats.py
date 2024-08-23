# /api/stats/entity
import time
import traceback

import jwt
from django.conf import settings

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity

METABASE_SITE_URL = "https://metabase.carbure.beta.gouv.fr"


class StatsEntityError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    STATS_ENTITY_FAILED = "STATS_ENTITY_FAILED"
    STATS_DASHBOARD_TYPE_UNAVAILABLE = "STATS_DASHBOARD_TYPE_UNAVAILABLE"


def get_metabase_dashboard(type: str):
    if type == Entity.PRODUCER:
        return 207
    if type == Entity.OPERATOR:
        return 205
    # TODO add when ready
    # if type == Entity.TRADER :
    #     return 211
    # if type == Entity.AUDITOR :
    #     return 210
    return 0


@check_user_rights()
def get_entity_stats(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
    except:
        traceback.print_exc()
        return ErrorResponse(400, StatsEntityError.MALFORMED_PARAMS)

    try:
        entity = Entity.objects.get(id=entity_id)
        dashboard_id = get_metabase_dashboard(entity.entity_type)

    except:
        traceback.print_exc()
        return ErrorResponse(400, StatsEntityError.STATS_DASHBOARD_TYPE_UNAVAILABLE)

    if dashboard_id == 0:
        traceback.print_exc()
        return ErrorResponse(400, StatsEntityError.STATS_DASHBOARD_TYPE_UNAVAILABLE)

    try:
        payload = {
            "resource": {"dashboard": dashboard_id},
            "params": {"entity_id": [entity_id]},
            "exp": round(time.time()) + (60 * 10),
        }
        token = jwt.encode(payload, settings.METABASE_SECRET_KEY, algorithm="HS256")
        iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=false&titled=false"
        return SuccessResponse({"metabase_iframe_url": iframeUrl})
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, StatsEntityError.STATS_ENTITY_FAILED)
