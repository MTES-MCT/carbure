from django.utils.decorators import decorator_from_middleware, method_decorator
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.filters import FiltersActionFactory
from core.utils import CustomPageNumberPagination
from traceability.exceptions import ActionNotDeletableError
from traceability.filters import ActionFilter
from traceability.handlers.action import ActionIndustryHandler
from traceability.middlewares import ActionHandlerMiddleware
from traceability.models import Action
from traceability.serializers.action import ActionQuerySerializer, ActionSerializer
from traceability.serializers.action_authorization import ActionAuthorizationSerializer
from traceability.services.delete import delete_action
from traceability.services.inherited_fields import attach_inherited_fields
from traceability.services.parent_chain import annotate_parent_chain
from traceability.services.quantities import attach_quantities
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
            action = annotate_parent_chain(self.get_queryset().filter(pk=action.pk)).get()
            attach_inherited_fields([action])
            attach_quantities([action])
        return action

    def paginate_queryset(self, queryset):
        page = super().paginate_queryset(queryset)
        if not page:
            return page

        # The walk runs on the page ids. MySQL rejects LIMIT inside the CTE.
        # origin_material has already reduced this queryset to the matching ids.
        ids = [action.pk for action in page]
        annotated = annotate_parent_chain(queryset.filter(pk__in=ids))
        actions_by_id = {action.pk: action for action in annotated}
        actions = [actions_by_id[pk] for pk in ids]
        return attach_quantities(attach_inherited_fields(actions))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = getattr(self.request, "entity", None)
        context["handler"] = getattr(self.request, "handler", None)
        return context

    @extend_schema(
        request=ActionAuthorizationSerializer,
        responses={201: ActionSerializer, 400: None, 403: None},
        description="Create an action.",
    )
    def create(self, request, *args, **kwargs):
        context = self.get_serializer_context()
        authorization = ActionAuthorizationSerializer(data=request.data, context=context)
        authorization.is_valid(raise_exception=True)

        action_type = authorization.validated_data["type"]
        serializer_class = request.handler.get_action_creation_serializers().get(action_type)
        if serializer_class is None:
            raise ValidationError({"type": _("Ce type d'action ne peut pas être créé.")})

        serializer = serializer_class(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def perform_destroy(self, instance):
        try:
            delete_action(instance)
        except ActionNotDeletableError as exc:
            raise ValidationError() from exc
