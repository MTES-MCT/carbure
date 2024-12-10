from django.db.models.query_utils import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from core.models import Entity, UserRights
from doublecount.models import DoubleCountingApplication
from doublecount.permissions import HasAdminRights
from doublecount.serializers import DoubleCountingApplicationSerializer
from doublecount.views.applications.mixins import ActionMixin
from saf.permissions import HasUserRights


class ApplicationViewSet(ActionMixin, RetrieveModelMixin, GenericViewSet):
    queryset = applications = DoubleCountingApplication.objects.filter(~Q(status__in=[DoubleCountingApplication.ACCEPTED]))
    serializer_class = DoubleCountingApplicationSerializer
    pagination_class = None
    lookup_field = "id"
    permission_classes = (
        IsAuthenticated,
        HasUserRights(None, [Entity.PRODUCER, Entity.ADMIN]),
    )

    def get_permissions(self):
        # TODO fix permissions if needed
        if self.action == "add":
            return [IsAuthenticated(), HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.PRODUCER, Entity.ADMIN])]
        # if self.action == "agreements_public_list":
        #     return [AllowAny()]
        if self.action in ["list_admin", "export", "approve"]:
            return [HasAdminRights()]

        return super().get_permissions()

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
        responses=DoubleCountingApplicationSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
