from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets

from core.filters import FiltersActionFactory
from core.permissions import HasEntityReadRights, HasEntityWriteRights
from traceability.filters import ActionFilter
from traceability.models import Action
from traceability.serializers import ActionInputSerializer, ActionSerializer
from traceability.views.mixins import YearsActionMixin


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
    ]
)
class ActionViewset(YearsActionMixin, FiltersActionFactory(), viewsets.ModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [HasEntityReadRights]
    filterset_class = ActionFilter
    search_fields = ["pos_id"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [HasEntityWriteRights()]
        return super().get_permissions()

    def get_queryset(self):
        return self.queryset.filter(Q(holder=self.request.entity) | Q(parent__holder=self.request.entity))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ActionInputSerializer
        return ActionSerializer
