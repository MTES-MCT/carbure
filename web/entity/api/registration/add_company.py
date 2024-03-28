from urllib import request
from django import forms

from core.carburetypes import CarbureError
from core.decorators import otp_or_403
from core.models import EntityCertificate, GenericCertificate, Entity, Pays, UserRightsRequests
from core.common import SuccessResponse, ErrorResponse
from django.core.mail import send_mail
from django.conf import settings

from datetime import datetime

class ApplyForNewCompanyError:
    COMPANY_NAME_ALREADY_USED = "COMPANY_NAME_ALREADY_USED"


class ApplyForNewCompanyForm(forms.Form):
    activity_description = forms.CharField(max_length=256, required=True)
    certificate_id = forms.CharField(max_length=64, required=True)
    certificate_type = forms.CharField(max_length=32, required=True)
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


@otp_or_403
def apply_for_new_company(request, *args, **kwargs):

    form = ApplyForNewCompanyForm(request.POST)

    if not form.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, form.errors)

    activity_description = form.cleaned_data["activity_description"]
    certificate_id = form.cleaned_data["certificate_id"]
    certificate_type = form.cleaned_data["certificate_type"]
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

    duplicated_company = Entity.objects.filter(name=name).first()
    if duplicated_company:
        return ErrorResponse(400, ApplyForNewCompanyError.COMPANY_NAME_ALREADY_USED)

    entity = Entity.objects.create(
        activity_description=activity_description,
        entity_type=entity_type,
        legal_name=legal_name,
        name=legal_name,
        registered_address=registered_address,
        registered_city=registered_city,
        registered_country=registered_country,
        registered_zipcode=registered_zipcode,
        registration_id=registration_id,
        sustainability_officer=sustainability_officer,
        sustainability_officer_email=sustainability_officer_email,
        sustainability_officer_phone_number=sustainability_officer_phone_number,
    )

    # add certificat
    original_certificate = GenericCertificate.objects.get(certificate_type=certificate_type, certificate_id=certificate_id)
    EntityCertificate.objects.create(entity=entity, certificate=original_certificate)

    # add right request
    UserRightsRequests.objects.update_or_create(
        user=request.user, entity=entity, defaults={"role": Entity.ADMIN, "status": "PENDING"}
    )


    #send email to user
    today = datetime.now().strftime("%d/%m/%Y")
    text_message = f"""
    Bonjour,

    Votre demande d'inscription pour la société {entity.name} a bien enregistrée à la date du {today}. 
    L'équipe de la DGEC va étudier votre demande et vous serez notifié lorsque celle-ci aura été traitée.
    
    Bien cordialement,
    L'équipe CarbuRe
    """
    send_mail(
        subject="[CarbuRe] Demande d'inscription de société enregistrée",
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=False,
    )

    #send email to staff
    admin_link = f"https://carbure.beta.gouv.fr/admin/core/entity/{entity.id}/change/"
    text_message = f"""
    Hello, ça Carbure ?!

    Une demande d'inscription de société {entity.name} a été déposé le {today} par l'utilisateur {request.user.email}. 
    Veuillez traiter cette demande dans l'interface administrateur de CarbuRe {admin_link}.
    
    Bonne journée
    """
    send_mail(
        subject="[CarbuRe] Demande d'inscription de la société " + entity.name  ,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["carbure@beta.gouv.fr"],
        fail_silently=False,
    )

    return SuccessResponse()


