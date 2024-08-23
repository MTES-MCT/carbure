from datetime import datetime

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import otp_or_403
from core.models import Entity, EntityCertificate, GenericCertificate, Pays, UserRightsRequests
from core.utils import CarbureEnv


class ApplyForNewCompanyError:
    COMPANY_NAME_ALREADY_USED = "COMPANY_NAME_ALREADY_USED"


class ApplyForNewCompanyForm(forms.Form):
    activity_description = forms.CharField(max_length=5000, required=True)
    entity_type = forms.CharField(max_length=64, required=True)
    name = forms.CharField(max_length=128, required=True)
    legal_name = forms.CharField(max_length=128, required=True)
    registered_address = forms.CharField(max_length=256, required=True)
    registered_city = forms.CharField(max_length=64, required=True)
    registered_country_code = forms.ModelChoiceField(queryset=Pays.objects.all(), to_field_name="code_pays", required=False)
    registered_zipcode = forms.CharField(max_length=64, required=True)
    registration_id = forms.CharField(max_length=9, required=True)  # SIREN
    sustainability_officer = forms.CharField(max_length=64, required=True)
    sustainability_officer_email = forms.CharField(max_length=254, required=True)
    sustainability_officer_phone_number = forms.CharField(max_length=32, required=True)
    website = forms.URLField(required=False)
    vat_number = forms.CharField(max_length=32, required=False)
    certificate_id = forms.CharField(max_length=64, required=False)
    certificate_type = forms.CharField(max_length=32, required=False)


@otp_or_403
def add_company(request, *args, **kwargs):

    form = ApplyForNewCompanyForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    activity_description = form.cleaned_data["activity_description"]
    entity_type = form.cleaned_data["entity_type"]
    name = form.cleaned_data["name"]
    legal_name = form.cleaned_data["legal_name"]
    registered_address = form.cleaned_data["registered_address"]
    registered_city = form.cleaned_data["registered_city"]
    registered_country = form.cleaned_data["registered_country_code"]
    registered_zipcode = form.cleaned_data["registered_zipcode"]
    registration_id = form.cleaned_data["registration_id"]
    sustainability_officer = form.cleaned_data["sustainability_officer"]
    sustainability_officer_email = form.cleaned_data["sustainability_officer_email"]
    sustainability_officer_phone_number = form.cleaned_data["sustainability_officer_phone_number"]
    website = form.cleaned_data["website"]
    vat_number = form.cleaned_data["vat_number"]
    certificate_id = form.cleaned_data["certificate_id"]
    certificate_type = form.cleaned_data["certificate_type"]

    duplicated_company = Entity.objects.filter(name=name).first()
    if duplicated_company:
        return ErrorResponse(400, ApplyForNewCompanyError.COMPANY_NAME_ALREADY_USED)

    with transaction.atomic():
        entity = Entity.objects.create(
            activity_description=activity_description,
            entity_type=entity_type,
            legal_name=legal_name,
            name=name,
            registered_address=registered_address,
            registered_city=registered_city,
            registered_country=registered_country,
            registered_zipcode=registered_zipcode,
            registration_id=registration_id,
            sustainability_officer=sustainability_officer,
            sustainability_officer_email=sustainability_officer_email,
            sustainability_officer_phone_number=sustainability_officer_phone_number,
            is_enabled=False,
            website=website,
            vat_number=vat_number,
        )

        # add certificat
        if entity_type not in [Entity.AIRLINE, Entity.CPO] and certificate_id and certificate_type:
            original_certificate = GenericCertificate.objects.get(
                certificate_type=certificate_type, certificate_id=certificate_id
            )
            entity_certificat = EntityCertificate.objects.create(entity=entity, certificate=original_certificate)
            entity.default_certificate = entity_certificat.certificate.certificate_id
            entity.save()

        # add right request
        UserRightsRequests.objects.create(user=request.user, entity=entity, role=UserRightsRequests.ADMIN, status="PENDING")

        send_email_to_user(entity, request.user)
        send_email_to_dgec(entity, request.user)

        return SuccessResponse()


def send_email_to_user(entity, user):
    # send email to user
    today = datetime.now().strftime("%d/%m/%Y")
    subject = "Demande d'inscription de société enregistrée"
    subject = subject if CarbureEnv.is_prod else "TEST " + subject
    recipient_list = [user.email] if CarbureEnv.is_prod else ["carbure@beta.gouv.fr"]
    text_message = f"""
    Bonjour,

    Votre demande d'inscription pour la société {entity.name} a bien enregistrée à la date du {today}. 
    L'équipe de la DGEC va étudier votre demande et vous serez notifié lorsque celle-ci aura été traitée.
    
    Bien cordialement,
    L'équipe CarbuRe 
    """

    send_mail(
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )


def send_email_to_dgec(entity, user):
    today = datetime.now().strftime("%d/%m/%Y")
    subject = "Demande d'inscription de la société " + entity.name
    subject = subject if CarbureEnv.is_prod else "TEST " + subject

    recipient_list = ["carbure@beta.gouv.fr"]  # send to current user to avoid spam all the carbure team
    admin_link = f"{CarbureEnv.get_base_url()}/admin/core/entity/?is_enabled=False"
    text_message = f"""
    Bonjour,

    Une demande d'inscription de société {entity.name} a été déposé le {today} par l'utilisateur {user.email}. 
    Veuillez traiter cette demande dans l'interface administrateur de CarbuRe :

    1 - Visualisez la liste des sociétés à valider sur ce lien : {admin_link}.
    2 - Selectionnez la société {entity.name}.
    3 - Selectionnez l'action "Activer les sociétés sélectionnées".
    4 - Cliquez sur "Envoyer".
    
    Bonne journée
    """
    send_mail(
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
