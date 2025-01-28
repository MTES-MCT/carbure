from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import UserRightsRequests
from user.serializers.user import UserRightsRequestsSerializer as UserRightsRequestsSeriaizer

User = get_user_model()


class RightsRequestsActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
            OpenApiParameter(name="q", type=str, description="Search in user email or entity name."),
            OpenApiParameter(
                name="statuses",
                type={"type": "array", "items": {"type": "string"}},
                description="Comma-separated list of statuses (e.g., active,pending).",
            ),
            OpenApiParameter(name="company_id", type=int, description="Filter by entity ID."),
        ],
        responses=UserRightsRequestsSeriaizer(many=True),
    )
    @action(detail=False, methods=["get"], url_path="rights-requests")
    def rights_requests(self, request):
        q = self.request.query_params.get("q")
        statuses = self.request.query_params.getlist("statuses")
        company_id = self.request.query_params.get("company_id")
        requests = UserRightsRequests.objects.all()

        if company_id:
            requests = requests.filter(entity__id=company_id)
        if statuses:
            requests = requests.filter(status__in=statuses)
        if q:
            requests = requests.filter(Q(user__email__icontains=q) | Q(entity__name__icontains=q))

        requests_sez = UserRightsRequestsSeriaizer(instance=requests, many=True)  # [r.natural_key() for r in requests]
        return Response(requests_sez.data)
