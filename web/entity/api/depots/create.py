from django.views.decorators.http import require_POST
from core.models import UserRights
from core.decorators import check_user_rights
from entity.serializers.depot import DepotSerializer
from core.common import ErrorResponse, SuccessResponse
from core.carburetypes import CarbureError
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def create_depot(request, entity, entity_id):
    serializer = DepotSerializer(data=request.POST)

    if not serializer.is_valid():
        return ErrorResponse(400, CarbureError.MALFORMED_PARAMS, data=serializer.errors)

    serializer.save()

    send_email_to_user(entity, serializer.validated_data["name"], request.user)

    return SuccessResponse()


def send_email_to_user(entity, depot_name, user):
    # send email to user
    today = datetime.now().strftime("%d/%m/%Y")
    recipient_list = [user.email]
    text_message = f"""
    Bonjour,

    Votre demande d'ajout du dépôt {depot_name} a bien enregistrée à la date du {today}. 
    L'équipe de la DGEC va étudier votre demande et les administrateurs de l'entité {entity.name} seront notifiés une fois celle-ci validée.
    
    Bien cordialement,
    L'équipe CarbuRe 
    """

    send_mail(
        subject="Demande de création d'un dépôt enregistrée",
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
