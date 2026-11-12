from django.utils.decorators import decorator_from_middleware, method_decorator
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.filters import FiltersActionFactory
from core.utils import CustomPageNumberPagination
from traceability.exceptions import ActionNotDeletableError
from traceability.filters import ActionFilter
from traceability.handlers.action import ActionIndustryHandler
from traceability.middlewares import ActionHandlerMiddleware
from traceability.models import Action
from traceability.serializers.action import ActionQuerySerializer, ActionSerializer
from traceability.services.delete import delete_action
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
@method_decorator(decorator_from_middleware(ActionHandlerMiddleware), name="dispatch")
class ActionViewset(
    YearsActionMixin,
    ExcelTemplateActionMixin,
    ExcelImportActionMixin,
    FiltersActionFactory(),
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    filterset_class = ActionFilter
    pagination_class = CustomPageNumberPagination
    search_fields = ["holder__name", "pos_id"]

    def get_permissions(self):
        # prevent DRF from raising an exception when generating the schema
        handler = getattr(self.request, "handler", None) or ActionIndustryHandler()
        return handler.get_permissions(self.action)

    def get_queryset(self):
        return self.request.handler.scope_queryset(self.request, self.queryset)

    def get_object(self):
        action = super().get_object()
        if self.action == "retrieve":
            return Action.annotate_actions([action])[0]
        return action

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)
        if not page:
            return page

        # origin_material has already reduced this queryset to the matching ids.
        return Action.annotate_actions(page)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["handler"] = getattr(self.request, "handler", None)
        return context

    def perform_destroy(self, instance):
        try:
            delete_action(instance)
        except ActionNotDeletableError as exc:
            raise ValidationError() from exc
