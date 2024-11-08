from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_otp import user_has_device
from django_otp.plugins.otp_email.models import EmailDevice
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from auth.serializers import UserCreationSerializer
from auth.tokens import account_activation_token
from core.helpers import send_mail


class UserCreationAction:
    @extend_schema(
        request=UserCreationSerializer,
        examples=[
            OpenApiExample(
                "Example response.",
                status_codes=[200],
                value={"status": "success"},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = UserCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        subject = "Carbure - Activation de compte"
        self.send_email(user, request, subject)

        return Response({"status": "success"})

    def send_email(
        self,
        user,
        request,
        subject,
        email_type="account_activation_email",
        extra_context=None,
    ):
        if extra_context is None:
            extra_context = {}
        current_site = get_current_site(request)
        email_subject = subject
        email_context = {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        } | extra_context
        html_message = loader.render_to_string(f"emails/{email_type}.html", email_context)
        text_message = loader.render_to_string(f"emails/{email_type}.txt", email_context)
        send_mail(
            request=request,
            subject=email_subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            html_message=html_message,
            recipient_list=[user.email],
        )
        if not user_has_device(user):
            email_otp = EmailDevice()
            email_otp.user = user
            email_otp.name = "email"
            email_otp.confirmed = True
            email_otp.email = user.email
            email_otp.save()
