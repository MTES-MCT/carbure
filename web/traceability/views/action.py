from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets

from core.filters import FiltersActionFactory
from traceability.filters import ActionFilter
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.registry import get_action_handler
from traceability.models import Action
from traceability.serializers.action import ActionInputSerializer, ActionQuerySerializer, ActionSerializer
from traceability.views.mixins import ExcelImportActionMixin, ExcelTemplateActionMixin, YearsActionMixin


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="entity_id",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Authorised entity ID.",
            required=True,
        ),
        OpenApiParameter(
            name="year",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Filter actions by working date year.",
        ),
        ActionQuerySerializer,
    ]
)
class ActionViewset(
    YearsActionMixin, ExcelTemplateActionMixin, ExcelImportActionMixin, FiltersActionFactory(), viewsets.ModelViewSet
):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    filterset_class = ActionFilter
    search_fields = ["pos_id"]

    def initial(self, request, *args, **kwargs):
        query = ActionQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        request.handler = get_action_handler(query.validated_data["industry"])
        super().initial(request, *args, **kwargs)

    def get_permissions(self):
        # prevent DRF from raising an exception when generating the schema
        handler = getattr(self.request, "handler", None) or ActionIndustryHandler()
        return handler.get_permissions(self.action)

    def get_queryset(self):
        return self.queryset.filter(
            Q(holder=self.request.entity) | Q(parent__holder=self.request.entity),
            industry=self.request.handler.industry,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["handler"] = self.request.handler
        return context

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ActionInputSerializer
        return ActionSerializer
