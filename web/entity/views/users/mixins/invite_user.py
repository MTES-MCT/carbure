from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.views.mixins.register import send_email as send_registration_email
from core.models import Entity, UserRights, UserRightsRequests

User = get_user_model()


class InviteUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    role = serializers.CharField(required=True)

    def validate_role(self, value):
        """Ensure the role is valid."""
        if value not in dict(UserRights.ROLES):
            raise serializers.ValidationError("INVALID_ROLE")
        return value


class InviteUserError:
    INVALID_ROLE = "INVALID_ROLE"
    ACCESS_ALREADY_GIVEN = "ACCESS_ALREADY_GIVEN"
    INVITE_FAILED = "INVITE_FAILED"


class InviteUserActionMixin:
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
        request=InviteUserSerializer,
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
    @action(detail=False, methods=["post"], url_path="invite-user")
    def invite_user(self, request):
        entity_id = self.request.query_params.get("entity_id")

        entity = Entity.objects.get(id=entity_id)
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        role = serializer.validated_data.get("role")

        email = User.objects.normalize_email(email)

        try:
            user = User.objects.get(email=email)

            email_subject = "Carbure - Invitation à rejoindre une entité"
            email_type = "invite_user_email"

        except Exception:
            # Create a new user (non active) with a random password
            user = User.objects.create_user(
                email=email,
                password=User.objects.make_random_password(20),
                is_active=False,
            )
            user.save()

            email_subject = "Carbure - Invitation à rejoindre une entité"
            email_type = "account_activation_email"

        # Update rights and requests
        check_user_rights = UserRights.objects.filter(user=user, entity=entity).first()
        if check_user_rights:
            return Response(
                {"message": InviteUserError.ACCESS_ALREADY_GIVEN},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            UserRightsRequests.objects.update_or_create(
                user=user, entity=entity, defaults={"role": role, "status": "ACCEPTED"}
            )
            UserRights.objects.create(user=user, entity=entity, role=role)

        except Exception:
            return Response(
                {"message": InviteUserError.INVITE_FAILED},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Send email
        email_context = {"invitation": True, "entity_name": entity.name}
        send_registration_email(user, request, email_subject, email_type, email_context)

        return Response({"status": "success"})
