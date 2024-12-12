from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity, UserRights, UserRightsRequests
from entity.serializers import (
    UserRightsRequestsSeriaizer,
    UserRightsResponseSeriaizer,
    UserRightsSeriaizer,
)


class EntityRightsRequestsActionMixin:
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
        responses=UserRightsResponseSeriaizer,
    )
    @action(detail=False, methods=["get"], url_path="entity-rights-requests")
    def entity_rights_requests(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        rights = UserRights.objects.filter(entity=entity)
        requests = UserRightsRequests.objects.filter(entity=entity, status__in=["PENDING", "ACCEPTED"])
        # hide users of the Carbure staff
        if not request.user.is_staff:
            rights = rights.filter(user__is_staff=False, user__is_superuser=False)
            requests = requests.filter(user__is_staff=False, user__is_superuser=False)

        data = {}
        data["rights"] = UserRightsSeriaizer(instance=rights, many=True).data
        data["requests"] = UserRightsRequestsSeriaizer(instance=requests, many=True).data
        return Response(data)
