from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.models import Entity
from doublecount.filters import ApplicationFilter
from doublecount.models import DoubleCountingApplication
from doublecount.permissions import HasDoubleCountingAdminRights, HasProducerRights, HasProducerWriteRights
from doublecount.serializers import DoubleCountingApplicationSerializer
from doublecount.views.applications.mixins import ActionMixin


class ApplicationViewSet(ActionMixin, RetrieveModelMixin, GenericViewSet):
    queryset = DoubleCountingApplication.objects.all()
    serializer_class = DoubleCountingApplicationSerializer
    pagination_class = None
    lookup_field = "id"
    filterset_class = ApplicationFilter
    permission_classes = [HasProducerRights | HasDoubleCountingAdminRights]

    def get_permissions(self):
        if self.action in ["check_file", "add", "upload_files", "delete_file"]:
            return [HasProducerWriteRights()]
        if self.action in ["list_admin", "export", "approve", "reject", "generate_decision", "update_approved_quotas"]:
            return [HasDoubleCountingAdminRights()]

        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        entity = self.request.entity

        if entity.entity_type == Entity.PRODUCER:
            queryset = DoubleCountingApplication.objects.filter(producer=entity)

        queryset = queryset.select_related("production_site").prefetch_related("production")
        return queryset

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
