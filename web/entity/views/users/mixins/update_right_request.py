from django.conf import settings
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from core.helpers import send_mail
from core.models import UserRights, UserRightsRequests
from core.utils import CarbureEnv


class UpdateRightsRequestsSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=UserRightsRequests.objects.all())
    status = serializers.ChoiceField(choices=UserRightsRequests.STATUS_TYPES)


class UpdateRightsRequestsActionMixin:
    @extend_schema(
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
            # send_mail
            email_subject = "Carbure - Demande acceptée"
            message = """
            Bonjour,

            Votre demande d'accès à la Société %s vient d'être validée par l'administration.

            """ % (right_request.entity.name)
            recipient_list = [right_request.user.email] if CarbureEnv.is_prod else ["carbure@beta.gouv.fr"]
            send_mail(
                request=request,
                subject=email_subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
            )
        else:
            UserRights.objects.filter(entity=right_request.entity, user=request.user).delete()
        return Response({"status": "success"})
