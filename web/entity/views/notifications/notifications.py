from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from core.models import CarbureNotification
from core.serializers import CarbureNotificationSerializer
from saf.permissions import HasUserRights


class NotificationSerializer(serializers.Serializer):
    notification_ids = serializers.PrimaryKeyRelatedField(
        queryset=CarbureNotification.objects.all(),
        many=True,
        error_messages={
            "does_not_exist": "One or more notifications do not exist.",
            "required": "You must provide a list of notifications.",
        },
    )

    def __init__(self, *args, **kwargs):
        entity_id = kwargs.pop("entity_id", None)
        super().__init__(*args, **kwargs)
        if entity_id:
            self.fields["notification_ids"].queryset = CarbureNotification.objects.filter(dest_id=entity_id)


class NotificationViewSet(ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CarbureNotificationSerializer
    pagination_class = None
    permission_classes = [HasUserRights()]

    def get_queryset(self):
        return CarbureNotification.objects.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        responses=CarbureNotificationSerializer(many=True),
    )
    def list(self, request):
        entity_id = self.request.query_params.get("entity_id")
        notifications = self.get_queryset()

        notifications = notifications.filter(dest_id=entity_id).order_by("-datetime")[0:15]
        serializer = CarbureNotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
        ],
        request=NotificationSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success", "updated_count": 0},
                description="Request successful.",
            ),
            400: OpenApiResponse(
                response={"message": ""},
                description="Bad request.",
            ),
        },
        examples=[
            OpenApiExample(
                "Success example",
                value={"status": "success", "updated_count": 0},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Bad request",
                value={"message": ""},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="ack")
    def ack(self, request):
        entity_id = self.request.query_params.get("entity_id")
        serializer = NotificationSerializer(data=request.data, entity_id=entity_id)
        if serializer.is_valid():
            notifications = serializer.validated_data["notifications"]

            notifications.update(acked=True)

            return Response({"status": "success", "updated_count": notifications.count()})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
