from django.utils.decorators import decorator_from_middleware, method_decorator
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.filters import FiltersActionFactory
from core.utils import CustomPageNumberPagination
from traceability.exceptions import ActionNotDeletableError
from traceability.filters import ActionFilter
from traceability.handlers.action import ActionIndustryHandler
from traceability.middlewares import ActionHandlerMiddleware
from traceability.models import Action, ActionStatus
from traceability.models.action import annotate_latest_status
from traceability.serializers.action import ActionDetailSerializer, ActionQuerySerializer, ActionSerializer
from traceability.services.delete import delete_action
from traceability.services.inherited_fields import attach_inherited_fields
from traceability.services.parent_chain import annotate_parent_chain
from traceability.services.quantities import attach_quantities
from traceability.views.mixins import ExcelImportActionMixin, ExcelTemplateActionMixin, YearsActionMixin

# A status lookup is about 0.003 ms. 100 000 rows stay around 300 ms.
# Above that, filtering or sorting by status walks too many actions.
STATUS_FILTER_MAX_ROWS = 100_000


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

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ActionDetailSerializer
        return ActionSerializer

    @extend_schema(responses=ActionDetailSerializer)
    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data)

    # @action is required. Overriding the mixin method without it drops the route,
    # and every filter dropdown then 404s.
    @action(methods=["get"], detail=False)
    def filters(self, request):
        # status uses a custom method, so the mixin does not list it.
        # Above the ceiling the six values are returned without reading action_status.
        # Under it, the options are the statuses present on the already filtered queryset.
        if request.query_params.get("filter") == "status":
            return Response(self._status_filter_options())
        return super().filters(request)

    def _status_filter_options(self):
        queryset = self._queryset_without_status(self.get_queryset())
        if queryset.count() > STATUS_FILTER_MAX_ROWS:
            return [value for value, _label in ActionStatus.STATUSES]
        statuses = annotate_latest_status(queryset).values_list("status", flat=True).distinct().order_by("status")
        return [value for value in statuses if value is not None]

    def get_queryset(self):
        queryset = self.request.handler.scope_queryset(self.request, self.queryset)
        if self.action in ("retrieve", "destroy"):
            return queryset.with_status()
        # The page annotates status for the rows it returns. The whole queryset
        # gets it only when a filter or a sort needs it and the other filters
        # have already left few enough rows.
        if self.action == "list" and self._requests_status() and self._status_queryset_is_small(queryset):
            return queryset.with_status()
        return queryset

    def _requests_status(self) -> bool:
        params = self.request.query_params
        if params.get("status"):
            return True
        return self._orders_by_status(params.getlist("order_by"))

    def _status_queryset_is_small(self, queryset) -> bool:
        return self._queryset_without_status(queryset).count() <= STATUS_FILTER_MAX_ROWS

    def _queryset_without_status(self, queryset):
        params = self.request.query_params.copy()
        params.pop("status", None)
        kept_orders = []
        for raw in params.getlist("order_by"):
            kept = [part.strip() for part in raw.split(",") if part.strip().lstrip("-") != "status"]
            if kept:
                kept_orders.append(",".join(kept))
        if kept_orders:
            params.setlist("order_by", kept_orders)
        else:
            params.pop("order_by", None)
        filtered = ActionFilter(data=params, queryset=queryset, request=self.request).qs
        return SearchFilter().filter_queryset(self.request, filtered, self)

    @staticmethod
    def _orders_by_status(order_by: list[str]) -> bool:
        for raw in order_by:
            if any(part.strip().lstrip("-") == "status" for part in raw.split(",")):
                return True
        return False

    def get_object(self):
        action = super().get_object()
        if self.action == "retrieve":
            action = annotate_latest_status(annotate_parent_chain(self.get_queryset().filter(pk=action.pk))).get()
            attach_inherited_fields([action])
            attach_quantities([action])
        return action

    def paginate_queryset(self, queryset):
        # select_related joins every related row before LIMIT. MySQL then starts
        # from entities, writes all matching actions to a temporary table, and
        # only afterwards keeps 100. The page query reads ids alone. Relations
        # are loaded below, for those ids.
        page = super().paginate_queryset(queryset.select_related(None).values("pk"))
        if not page:
            return page

        # The walk runs on the page ids. MySQL rejects LIMIT inside the CTE.
        # origin_material has already reduced this queryset to the matching ids.
        ids = [row["pk"] for row in page]
        annotated = annotate_latest_status(annotate_parent_chain(queryset.filter(pk__in=ids)))
        actions_by_id = {action.pk: action for action in annotated}
        actions = [actions_by_id[pk] for pk in ids]
        return attach_quantities(attach_inherited_fields(actions))

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
