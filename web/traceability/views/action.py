from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets

from core.filters import FiltersActionFactory
from traceability.filters import ActionFilter
from traceability.handlers import get_action_handler
from traceability.models import Action
from traceability.serializers.action import ActionInputSerializer, ActionQuerySerializer, ActionSerializer
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
        ActionQuerySerializer,
    ]
)
class ActionViewset(YearsActionMixin, FiltersActionFactory(), viewsets.ModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    filterset_class = ActionFilter
    search_fields = ["pos_id"]

    def get_handler(self):
        query = ActionQuerySerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)
        return get_action_handler(query.validated_data["industry"])

    def get_permissions(self):
        handler = self.get_handler()

        return handler.get_permissions(self.action)

    def get_queryset(self):
        return self.queryset.filter(
            Q(holder=self.request.entity) | Q(parent__holder=self.request.entity),
            industry=self.get_handler().industry,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        return context

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ActionInputSerializer
        return ActionSerializer
