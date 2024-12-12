import time
import traceback

import jwt
from django.conf import settings
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity

METABASE_SITE_URL = "https://metabase.carbure.beta.gouv.fr"


class StatsEntityError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    STATS_ENTITY_FAILED = "STATS_ENTITY_FAILED"
    STATS_DASHBOARD_TYPE_UNAVAILABLE = "STATS_DASHBOARD_TYPE_UNAVAILABLE"


def get_metabase_dashboard(entity_type: str):
    if entity_type == Entity.PRODUCER:
        return 207
    if entity_type == Entity.OPERATOR:
        return 205
    # TODO: Add when ready
    # if entity_type == Entity.TRADER:
    #     return 211
    # if entity_type == Entity.AUDITOR:
    #     return 210
    return 0


class EntityStatsActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response={"metabase_iframe_url": f"{METABASE_SITE_URL}/embed/dashboard/...#bordered=false&titled=false"},
                description="Request successful.",
            ),
            400: OpenApiResponse(
                response={"message": ""},
                description="Bad request.",
            ),
        },
        examples=[
            OpenApiExample(
                "Success example",
                value={"metabase_iframe_url": f"{METABASE_SITE_URL}/embed/dashboard/...#bordered=false&titled=false"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad request",
                value={"message": ""},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="stats")
    def get_entity_stats(self, request):
        entity_id = request.query_params.get("entity_id")

        try:
            entity = Entity.objects.get(id=entity_id)
            dashboard_id = get_metabase_dashboard(entity.entity_type)

        except Exception:
            traceback.print_exc()
            return Response(
                {"message": StatsEntityError.STATS_DASHBOARD_TYPE_UNAVAILABLE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if dashboard_id == 0:
            traceback.print_exc()
            return Response(
                {"message": StatsEntityError.STATS_DASHBOARD_TYPE_UNAVAILABLE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = {
                "resource": {"dashboard": dashboard_id},
                "params": {"entity_id": [entity_id]},
                "exp": round(time.time()) + (60 * 10),
            }
            token = jwt.encode(payload, settings.METABASE_SECRET_KEY, algorithm="HS256")
            iframe_url = f"{METABASE_SITE_URL}/embed/dashboard/{token}#bordered=false&titled=false"
            return Response({"metabase_iframe_url": iframe_url})
        except Exception:
            traceback.print_exc()
            return Response(
                {"message": StatsEntityError.STATS_ENTITY_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )
