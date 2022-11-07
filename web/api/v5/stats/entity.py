# /api/v5/stats/entity
import jwt
import time
import traceback

from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights


METABASE_SITE_URL = "https://metabase.carbure.beta.gouv.fr"
METABASE_SECRET_KEY = ""


class StatsEntityError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    STATS_ENTITY_FAILED = "STATS_ENTITY_FAILED"

@check_user_rights()
def get_entity(request, *args, **kwargs):
    try:
        entity_id = int(kwargs["context"]["entity_id"])
    except:
        traceback.print_exc()
        return ErrorResponse(400, StatsEntityError.MALFORMED_PARAMS)

    try:
        payload = {
        "resource": {"dashboard": 204},
        "params": {
            "entity_id": [entity_id]
        },
        "exp": round(time.time()) + (60 * 10) # 10 minute expiration
        }
        token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")
        iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=false&titled=false"
        return SuccessResponse({"metabase_iframe_url" : iframeUrl})
    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, StatsEntityError.STATS_ENTITY_FAILED)
