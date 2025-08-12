from django.conf import settings
from django.template import loader
from django.utils import timezone
from django.utils.translation import gettext as _
from django_otp.plugins.otp_email.models import EmailDevice
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import CharField

from auth.serializers import ChangeEmailErrors, ConfirmEmailChangeSerializer, RequestEmailChangeSerializer
from core.helpers import send_mail
from core.utils import CarbureEnv


def create_email_change_device(user, new_email):
    EmailDevice.objects.filter(user=user, name__startswith="email_change_").delete()

    device = EmailDevice()
    device.user = user
    device.name = f"email_change_{new_email}"
    device.email = new_email
    device.confirmed = False
    device.save()
    device.generate_token(valid_secs=settings.OTP_EMAIL_TOKEN_VALIDITY)
    return device


def get_email_change_device(user, new_email):
    try:
        return EmailDevice.objects.get(user=user, name=f"email_change_{new_email}", confirmed=False)
    except EmailDevice.DoesNotExist:
        return None


def send_email_change_token(request, device, new_email):
    email_subject = _("Carbure - Confirmation de changement d'email")
    device_validity = timezone.localtime(device.valid_until)
    expiry = "%s %s" % (device_validity.strftime("%H:%M"), device_validity.tzname())

    email_context = {
        "user": request.user,
        "domain": CarbureEnv.get_base_url(),
        "otp_token": device.token,
        "token_expiry": expiry,
        "new_email": new_email,
    }

    html_message = loader.render_to_string("emails/email_change_otp.html", email_context)
    text_message = loader.render_to_string("emails/email_change_otp.txt", email_context)

    send_mail(
        request=request,
        subject=email_subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=html_message,
        recipient_list=[new_email],
    )


class ChangeEmailActionMixin:
    @extend_schema(
        request=RequestEmailChangeSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="RequestEmailChangeSuccess",
                    fields={"status": CharField(default="otp_sent")},
                ),
                description="Code OTP envoyé avec succès à la nouvelle adresse email",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=inline_serializer(
                    name="RequestEmailChangeError",
                    fields={
                        "message": CharField(help_text="Message d'erreur général", required=False),
                        "errors": CharField(help_text="Détails des erreurs de validation", required=False),
                    },
                ),
                description="Erreurs possibles: données invalides, mot de passe incorrect, email déjà utilisé",
            ),
        },
        examples=[
            OpenApiExample(
                "Succès",
                value={"status": "otp_sent"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Erreur de validation",
                value={
                    "message": ChangeEmailErrors.INVALID_DATA,
                    "errors": {
                        "new_email": ["Cette adresse email est déjà utilisée par un autre compte."],
                        "password": ["Mot de passe incorrect."],
                    },
                },
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="request-email-change")
    def request_email_change(self, request):
        try:
            serializer = RequestEmailChangeSerializer(data=request.data, context={"request": request})

            if not serializer.is_valid():
                return Response(
                    {"message": ChangeEmailErrors.INVALID_DATA, "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            new_email = serializer.validated_data["new_email"]

            device = create_email_change_device(request.user, new_email)
            send_email_change_token(request, device, new_email)

            return Response({"status": "otp_sent"})
        except Exception as e:
            import traceback

            traceback.print_exc()
            return Response({"error": f"Erreur interne: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        request=ConfirmEmailChangeSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name="ConfirmEmailChangeSuccess",
                    fields={"status": CharField(default="success")},
                ),
                description="Email mis à jour avec succès",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=inline_serializer(
                    name="ConfirmEmailChangeError",
                    fields={
                        "message": CharField(help_text="Message d'erreur général", required=False),
                        "errors": CharField(help_text="Détails des erreurs de validation", required=False),
                        "error": CharField(help_text="Code d'erreur spécifique", required=False),
                    },
                ),
                description="Erreurs possibles: données invalides, aucune demande en cours, code expiré, code incorrect",
            ),
        },
        examples=[
            OpenApiExample(
                "Succès",
                value={"status": "success"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Code incorrect",
                value={"error": ChangeEmailErrors.INVALID_OTP},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Code expiré",
                value={"error": ChangeEmailErrors.OTP_CODE_EXPIRED},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Aucune demande en cours",
                value={"error": ChangeEmailErrors.NO_CHANGE_REQUEST},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    @action(detail=False, methods=["post"], url_path="confirm-email-change")
    def confirm_email_change(self, request):
        serializer = ConfirmEmailChangeSerializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return Response(
                {"message": ChangeEmailErrors.INVALID_DATA, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        new_email = serializer.validated_data["new_email"]
        otp_token = serializer.validated_data["otp_token"]

        device = get_email_change_device(request.user, new_email)
        if not device:
            return Response(
                {"error": ChangeEmailErrors.NO_CHANGE_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if timezone.now() > device.valid_until:
            device.delete()
            return Response({"error": ChangeEmailErrors.OTP_CODE_EXPIRED}, status=status.HTTP_400_BAD_REQUEST)

        if device.token != otp_token:
            return Response({"error": ChangeEmailErrors.INVALID_OTP}, status=status.HTTP_400_BAD_REQUEST)

        request.user.email = new_email
        request.user.save()

        device.delete()

        try:
            main_device = EmailDevice.objects.get(user=request.user, name="email")
            main_device.email = new_email
            main_device.save()
        except EmailDevice.DoesNotExist:
            pass

        return Response({"status": "success"})
