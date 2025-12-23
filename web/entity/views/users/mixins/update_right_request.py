from django.conf import settings
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from core.helpers import send_mail
from core.models import UserRights, UserRightsRequests


class UpdateRightsRequestsSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=UserRightsRequests.objects.all())
    status = serializers.ChoiceField(choices=UserRightsRequests.STATUS_TYPES)


class UpdateRightsRequestsActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        request=UpdateRightsRequestsSerializer,
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
    @staticmethod
    def send_rights_update_notification(request):
        email_subject = "Carbure - Demande acceptée"
        message = f"""\
        Bonjour,

        Votre demande d'accès à la Société {request.entity.name} vient d'être validée par l'administration.

        """
        recipient_list = ["carbure@beta.gouv.fr"] if settings.WITH_EMAIL_DECORATED_AS_TEST else [request.user.email]

        send_mail(
            request=request,
            subject=email_subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
        )

    @action(detail=False, methods=["post"], url_path="update-right-request")
    def update_right_request(self, request):
        serializer = UpdateRightsRequestsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        right_request = serializer.validated_data.get("id")
        status = serializer.validated_data.get("status")

        right_request.status = status
        right_request.save()

        if status == "ACCEPTED":
            UserRights.objects.update_or_create(
                entity=right_request.entity,
                user=right_request.user,
                defaults={
                    "role": right_request.role,
                    "expiration_date": right_request.expiration_date,
                },
            )
            self.send_rights_update_notification(right_request)
        else:
            UserRights.objects.filter(entity=right_request.entity, user=request.user).delete()
        return Response({"status": "success"})
