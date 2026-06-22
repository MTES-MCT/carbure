from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from stock_poc.filters import ActionFilter
from stock_poc.models import Action
from stock_poc.permissions import HasStockPocRights
from stock_poc.serializers import ActionCreateSerializer, ActionSerializer
from stock_poc.services.balance import (
    available_for_certificates,
    available_for_consumption,
    with_available,
)


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
        request=None,
        responses={200: {"type": "object", "properties": {"deleted": {"type": "integer"}}}},
    )
    @action(detail=False, methods=["post"], url_path="reset")
    def reset(self, request):
        """Delete all POC actions (global reset for testing)."""
        deleted, _ = Action.objects.all().delete()
        return Response({"deleted": deleted}, status=status.HTTP_200_OK)
