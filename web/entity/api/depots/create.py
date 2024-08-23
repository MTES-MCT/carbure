from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

from core.carburetypes import CarbureError
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import UserRights
from core.utils import CarbureEnv
from entity.serializers.depot import DepotSerializer
from entity.services.geolocation import get_coordinates


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def create_depot(request, entity, entity_id):
    serializer = DepotSerializer(data=request.POST)

    if not serializer.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, data=serializer.errors)

    depot = serializer.save()

    depot.gps_coordinates = get_gps_coordinates(depot)
    depot.save()

    send_email_to_user(entity, depot.name, request.user)
    send_email_to_dgec(entity, depot.name, request.user)

    return SuccessResponse()


def get_gps_coordinates(depot):
    address = depot.address + " " + depot.postal_code + " " + depot.city + ", " + depot.country.name
    xy = get_coordinates(address)
    return f"{xy[0]},{xy[1]}" if xy else None


def send_email_to_user(entity, depot_name, user):
    today = datetime.now().strftime("%d/%m/%Y")
    recipient_list = [user.email]
    text_message = f"""
    Bonjour,

    Votre demande de création du dépôt {depot_name} pour la société {entity.name} a bien été enregistrée à la date du {today}. 
    L'équipe de la DGEC va étudier votre demande et vous serez notifiés lorsque celle-ci aura été traitée.
    
    Bien cordialement,
    L'équipe CarbuRe 
    """

    send_mail(
        subject="[CarbuRe][Demande d’ajout de dépôt enregistrée]",
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )


def send_email_to_dgec(entity, depot_name, user):
    today = datetime.now().strftime("%d/%m/%Y")
    recipient_list = ["carbure@beta.gouv.fr"]
    admin_link = f"{CarbureEnv.get_base_url()}/admin/core/depot/?is_enabled=False"
    text_message = f"""
    Bonjour,

    Une demande de création de dépôt {depot_name} pour la société {entity.name} a été déposé le {today} par l’utilisateur {user.email}.
    
    Veuillez traiter cette demande dans l'interface administrateur de CarbuRe :

    1 - Visualisez la liste des dépôts à valider sur ce lien : {admin_link}
    2 - Selectionnez le dépôt {depot_name}.
    3 - Selectionnez l'action "Valider les dépôts sélectionnés".
    4 - Cliquez sur "Envoyer".
    
    Bien à vous,
    CarbuRe
    """
    send_mail(
        subject="[CarbuRe][Nouvelle demande d’ajout de dépôt enregistrée]",
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
