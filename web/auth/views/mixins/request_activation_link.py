from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import UserResendActivationLinkSerializer
from auth.tokens import account_activation_token
from core.carburetypes import CarbureError
from core.helpers import send_mail


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
        serializer = UserResendActivationLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email", "")
        usermodel = get_user_model()
        try:
            user = usermodel.objects.get(email=email)
            current_site = get_current_site(request)
            email_subject = "Carbure - Activation de compte"
            email_context = {
                "user": user,
                "domain": current_site.domain,
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
            return Response({"status": "success"})
        except Exception:
            return Response(
                {"status": "error", "message": CarbureError.ACTIVATION_LINK_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )
