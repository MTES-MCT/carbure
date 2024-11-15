from django.conf import settings
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.decorators import otp_or_403
from core.helpers import send_mail
from core.models import UserRights, UserRightsRequests
from core.utils import CarbureEnv
from user.serializers import RequestAccessSerializer, ResponseSuccessSerializer


@extend_schema(
    examples=[
        OpenApiExample(
            "Example of response.",
            value={"status": "success"},
            request_only=False,
            response_only=True,
        ),
    ],
    request=RequestAccessSerializer,
    responses={200: ResponseSuccessSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@otp_or_403
def request_entity_access(request, *args, **kwargs):
    serializer = RequestAccessSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    entity = serializer.validated_data.get("entity_id")
    comment = serializer.validated_data.get("comment")
    role = serializer.validated_data.get("role")

    if request.user.is_staff:
        rr, _ = UserRightsRequests.objects.update_or_create(
            user=request.user,
            entity=entity,
            defaults={"comment": comment, "role": role, "status": "ACCEPTED"},
        )
        UserRights.objects.update_or_create(
            user=rr.user,
            entity=entity,
            defaults={"role": rr.role, "expiration_date": rr.expiration_date},
        )
    else:
        UserRightsRequests.objects.update_or_create(
            user=request.user,
            entity=entity,
            defaults={"comment": comment, "role": role, "status": "PENDING"},
        )

        validation_url = f"{CarbureEnv.get_base_url()}/org/{entity.id}/settings#users"
        email_subject = "Carbure - Demande d'accès"
        message = """
        Bonjour,
        Un utilisateur vient de faire une demande d'accès à CarbuRe.
        Vous pouvez valider ou refuser cette demande depuis la page d'administration de votre société : %s.

        Utilisateur: %s
        Société: %s
        Commentaire: %s
        """ % (
            validation_url,
            request.user.email,
            entity.name,
            comment,
        )

        # get all user admins for tthe entity
        admins = UserRights.objects.filter(entity=entity, role=UserRights.ADMIN).values_list("user__email", flat=True)
        recipient_list = list(admins)
        recipient_list.append("carbure@beta.gouv.fr")

        send_mail(
            request=request,
            subject=email_subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
        )

    return Response({"status": "success"})
