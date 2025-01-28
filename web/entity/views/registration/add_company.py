from datetime import datetime

from django.conf import settings
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.decorators import otp_or_403
from core.helpers import send_mail
from core.models import (
    Entity,
    EntityCertificate,
    GenericCertificate,
    Pays,
    UserRightsRequests,
)
from core.utils import CarbureEnv


class EntityCompanySerializer(serializers.ModelSerializer):
    registered_country_code = serializers.SlugRelatedField(
        queryset=Pays.objects.all(), slug_field="code_pays", required=False
    )
    certificate_type = serializers.ChoiceField(choices=GenericCertificate.CERTIFICATE_TYPES, required=False)
    certificate_id = serializers.CharField(required=False)

    class Meta:
        model = Entity
        fields = [
            "certificate_type",
            "certificate_id",
            "activity_description",
            "entity_type",
            "name",
            "legal_name",
            "registered_address",
            "registered_city",
            "registered_country_code",
            "registered_zipcode",
            "registration_id",
            "sustainability_officer",
            "sustainability_officer_email",
            "sustainability_officer_phone_number",
            "website",
            "vat_number",
        ]

    def validate(self, attrs):
        attrs.pop("certificate_type", None)
        attrs.pop("certificate_id", None)
        return attrs


class ApplyForNewCompanyError:
    COMPANY_NAME_ALREADY_USED = "COMPANY_NAME_ALREADY_USED"


@extend_schema(
    request=EntityCompanySerializer,
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
@api_view(["POST"])
@otp_or_403
def add_company_view(request):
    serializer = EntityCompanySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data
    name = validated_data.get("name")
    duplicated_company = Entity.objects.filter(name=name).first()
    if duplicated_company:
        return Response(
            {"message": ApplyForNewCompanyError.COMPANY_NAME_ALREADY_USED},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # with transaction.atomic():
    entity = Entity.objects.create(
        **validated_data,
        is_enabled=False,
    )

    # Gestion des certificats
    certificate_id = request.data.get("certificate_id")
    certificate_type = request.data.get("certificate_type")

    if validated_data["entity_type"] not in [Entity.AIRLINE, Entity.CPO] and certificate_id and certificate_type:
        try:
            original_certificate = GenericCertificate.objects.get(
                certificate_type=certificate_type, certificate_id=certificate_id
            )
            entity_certificate = EntityCertificate.objects.create(entity=entity, certificate=original_certificate)
            entity.default_certificate = entity_certificate.certificate.certificate_id
            entity.save()
        except GenericCertificate.DoesNotExist:
            return Response(
                {"error": "CERTIFICATE_NOT_FOUND"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Demande de droits
    UserRightsRequests.objects.create(
        user=request.user,
        entity=entity,
        role=UserRightsRequests.ADMIN,
        status="PENDING",
    )

    # Notifications par email
    send_email_to_user(entity, request)
    send_email_to_dgec(entity, request)

    return Response({"status": "success"})


def send_email_to_user(entity, request):
    # send email to user
    today = datetime.now().strftime("%d/%m/%Y")
    subject = "Demande d'inscription de société enregistrée"
    subject = subject if CarbureEnv.is_prod else "TEST " + subject
    recipient_list = [request.user.email] if CarbureEnv.is_prod else ["carbure@beta.gouv.fr"]
    text_message = f"""
    Bonjour,

    Votre demande d'inscription pour la société {entity.name} a bien enregistrée à la date du {today}.
    L'équipe de la DGEC va étudier votre demande et vous serez notifié lorsque celle-ci aura été traitée.

    Bien cordialement,
    L'équipe CarbuRe
    """

    send_mail(
        request=request,
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )


def send_email_to_dgec(entity, request):
    today = datetime.now().strftime("%d/%m/%Y")
    subject = "Demande d'inscription de la société " + entity.name
    subject = subject if CarbureEnv.is_prod else "TEST " + subject

    recipient_list = ["carbure@beta.gouv.fr"]  # send to current user to avoid spam all the carbure team
    admin_link = f"{CarbureEnv.get_base_url()}/admin/core/entity/?is_enabled=False"
    text_message = f"""
    Bonjour,

    Une demande d'inscription de société {entity.name} a été déposé le {today} par l'utilisateur {request.user.email}.
    Veuillez traiter cette demande dans l'interface administrateur de CarbuRe :

    1 - Visualisez la liste des sociétés à valider sur ce lien : {admin_link}.
    2 - Selectionnez la société {entity.name}.
    3 - Selectionnez l'action "Activer les sociétés sélectionnées".
    4 - Cliquez sur "Envoyer".

    Bonne journée
    """
    send_mail(
        request=request,
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )
