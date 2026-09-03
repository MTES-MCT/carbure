from django.db.models import Q
from django.utils.translation import gettext as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from core.filters import FiltersActionFactory
from core.pagination import TotalCountPagination
from traceability.filters import ActionFilter
from traceability.handlers.action import ActionIndustryHandler
from traceability.handlers.registry import get_action_handler
from traceability.models import Action
from traceability.serializers.action import ActionQuerySerializer, ActionSerializer
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

    def initial(self, request, *args, **kwargs):
        query = ActionQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        handler = get_action_handler(query.validated_data["industry"])
        quantity_unit = query.validated_data["quantity_unit"]
        if quantity_unit not in handler.units:
            raise ValidationError(
                {
                    "quantity_unit": _("Unité inconnue. Unités possibles : %(units)s")
                    % {"units": ", ".join(sorted(handler.units))}
                }
            )
        request.handler = handler
        request.quantity_unit = quantity_unit
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
        context["handler"] = getattr(self.request, "handler", None)
        context["quantity_unit"] = getattr(self.request, "quantity_unit", "MJ")
        return context
