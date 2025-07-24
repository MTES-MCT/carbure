from django.conf import settings
from django.contrib.auth import get_user_model
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import UserResendActivationLinkSerializer
from auth.tokens import account_activation_token
from core.helpers import send_mail
from core.utils import CarbureEnv


def email_from(data):
    serializer = UserResendActivationLinkSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data.get("email", "")


def retrieve_user(data):
    usermodel = get_user_model()
    email = email_from(data)
    return usermodel.objects.get(email__iexact=email)


def send_notification_mail(user, request):
    email_subject = "Carbure - Activation de compte"
    email_context = {
        "user": user,
        "domain": CarbureEnv.get_base_url(),
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": account_activation_token.make_token(user),
    }
    html_message = loader.render_to_string("emails/account_activation_email.html", email_context)
    text_message = loader.render_to_string("emails/account_activation_email.txt", email_context)
    send_mail(
        request=request,
        subject=email_subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=html_message,
        recipient_list=[user.email],
    )


class UserResendActivationLinkAction:
    @extend_schema(
        request=UserResendActivationLinkSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="request-activation-link")
    def request_activation_link(self, request):
        try:
            user = retrieve_user(request.data)
            send_notification_mail(user, request)
            return Response({"status": "success"})
        except Exception:
            return Response({"status": "success"})  # Do not expose user existence to avoid enumeration attacks
