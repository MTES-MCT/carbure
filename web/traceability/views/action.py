from django.utils.decorators import decorator_from_middleware, method_decorator
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.filters import FiltersActionFactory
from core.pagination import TotalCountPagination
from traceability.exceptions import ActionNotDeletableError
from traceability.filters import ActionFilter
from traceability.handlers.action import ActionIndustryHandler
from traceability.middlewares import ActionHandlerMiddleware
from traceability.models import Action
from traceability.serializers.action import ActionQuerySerializer, ActionSerializer
from traceability.services.delete import delete_action
from traceability.services.inherited_fields import attach_inherited_fields
from traceability.services.parent_chain import annotate_parent_chain
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
    pagination_class = TotalCountPagination
    search_fields = ["holder__name", "pos_id"]

    def get_permissions(self):
        # prevent DRF from raising an exception when generating the schema
        handler = getattr(self.request, "handler", None) or ActionIndustryHandler()
        return handler.get_permissions(self.action)

    def get_queryset(self):
        queryset = self.request.handler.scope_queryset(self.request, self.queryset)
        # Detail annotates the requested row only. List annotates after pagination.
        if self.action == "retrieve":
            queryset = annotate_parent_chain(queryset.filter(pk=self.kwargs["pk"]))
        return queryset

    def get_object(self):
        action = super().get_object()
        if self.action == "retrieve":
            attach_inherited_fields([action])
        return action

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)
        if not page:
            return page

        # The CTE runs on the page ids. MySQL rejects LIMIT in that subquery.
        ids = [action.pk for action in page]
        annotated = annotate_parent_chain(queryset.filter(pk__in=ids))

        # Re-index to keep page order.
        actions_by_id = {action.pk: action for action in annotated}
        actions = [actions_by_id[pk] for pk in ids]

        # Attach the inherited fields.
        return attach_inherited_fields(actions)

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
