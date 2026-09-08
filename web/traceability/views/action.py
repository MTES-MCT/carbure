from django.db.models import Q
from django.utils.decorators import decorator_from_middleware, method_decorator
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.filters import FiltersActionFactory
from core.pagination import TotalCountPagination
from traceability.filters import ActionFilter
from traceability.handlers.action import ActionIndustryHandler
from traceability.middlewares import ActionHandlerMiddleware
from traceability.models import Action
from traceability.serializers.action import ActionQuerySerializer, ActionSerializer
from traceability.services.total_emissions import annotate_total_emissions
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
    search_fields = ["pos_id"]

    def get_permissions(self):
        # prevent DRF from raising an exception when generating the schema
        handler = getattr(self.request, "handler", None) or ActionIndustryHandler()
        return handler.get_permissions(self.action)

    def get_queryset(self):
        queryset = self.queryset.filter(
            Q(holder=self.request.entity) | Q(parent__holder=self.request.entity),
            industry=self.request.handler.industry,
        )
        if self.action == "retrieve":
            queryset = annotate_total_emissions(queryset.filter(pk=self.kwargs["pk"]))
        return queryset

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)
        if page is None:
            return None
        # Annotate the current page only: the CTE cannot run on a sliced queryset
        # (MySQL rejects LIMIT in the pk__in subquery). Re-index to keep page order.
        ids = [action.pk for action in page]
        by_id = {action.pk: action for action in annotate_total_emissions(queryset.filter(pk__in=ids))}
        return [by_id[action_id] for action_id in ids]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["handler"] = getattr(self.request, "handler", None)
        return context
