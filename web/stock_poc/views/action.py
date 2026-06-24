from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Entity
from stock_poc.filters import ActionFilter
from stock_poc.models import Action
from stock_poc.permissions import HasStockPocRights
from stock_poc.serializers import (
    ActionCreateSerializer,
    ActionSerializer,
    QueryScenariosResponseSerializer,
)
from stock_poc.services.balance import (
    with_available,
)
from stock_poc.services.queries import run_scenarios


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
class ActionViewSet(ModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    filterset_class = ActionFilter
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = None

    def get_permissions(self):
        return [HasStockPocRights()]

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return ActionCreateSerializer
        return ActionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["entity"] = self.request.entity
        return context

    def get_queryset(self):
        return with_available(Action.objects.filter(owner=self.request.entity)).select_related("owner")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(ActionSerializer(instance).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(ActionSerializer(instance).data, status=status.HTTP_200_OK)

    @extend_schema(responses=ActionSerializer(many=True))
    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        """Flat list of all POC actions; the global tree is rebuilt on the frontend."""
        queryset = with_available(Action.objects.all()).select_related("owner")
        return Response(ActionSerializer(queryset, many=True).data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="query_entity_id",
                type=int,
                location=OpenApiParameter.QUERY,
                description=("Entity used for entity-scoped query scenarios. " "Defaults to entity_id when omitted."),
                required=False,
            ),
        ],
        responses=QueryScenariosResponseSerializer,
    )
    @action(detail=False, methods=["get"], url_path="queries")
    def queries(self, request):
        """Run all query scenarios from services/queries.py."""
        query_entity_id = request.query_params.get("query_entity_id")
        if query_entity_id is not None:
            try:
                query_entity = Entity.objects.get(pk=query_entity_id)
            except (Entity.DoesNotExist, ValueError):
                return Response(
                    {"detail": f"Entity #{query_entity_id} not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            query_entity = request.entity

        scenario_results = run_scenarios(entity=query_entity)
        payload = {
            "query_entity_id": query_entity.pk if query_entity else None,
            "scenarios": scenario_results,
        }
        return Response(QueryScenariosResponseSerializer(payload).data)

    @extend_schema(
        request=None,
        responses={200: {"type": "object", "properties": {"deleted": {"type": "integer"}}}},
    )
    @action(detail=False, methods=["post"], url_path="reset")
    def reset(self, request):
        """Delete all POC actions (global reset for testing)."""
        deleted, _ = Action.objects.all().delete()
        return Response({"deleted": deleted}, status=status.HTTP_200_OK)
