from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity, UserRights, UserRightsRequests

User = get_user_model()


class GrantAccessSerializer(serializers.Serializer):
    request_id = serializers.PrimaryKeyRelatedField(queryset=UserRightsRequests.objects.all())


class GrantAccessActionMixin:
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
        request=GrantAccessSerializer,
        responses={
            200: OpenApiResponse(
                response={"status": "success"},
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
                value={"status": "success"},
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
    @action(detail=False, methods=["post"], url_path="accept-user")
    def accept_user(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        serializer = GrantAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        right_request = serializer.validated_data.get("request_id")
        if right_request.entity.id != entity.id:
            # TODO: permission denieded
            pass

        try:
            right_request.status = "ACCEPTED"
            UserRights.objects.update_or_create(
                user=right_request.user,
                entity=entity,
                defaults={
                    "role": right_request.role,
                    "expiration_date": right_request.expiration_date,
                },
            )
            right_request.save()
        except Exception:
            return Response(
                {"message": "Could not create rights"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"status": "success"})
