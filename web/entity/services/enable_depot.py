from datetime import datetime

from django.conf import settings

from core.helpers import send_mail
from core.models import UserRights
from core.utils import CarbureEnv


def enable_depot(depot, request):
    if depot.is_enabled:
        return f"Le dépôt {depot.name} est déjà activé"

    depot.is_enabled = True
    depot.save()

    # Get entity admin users
    entity = depot.entity
    try:
        admins = UserRights.objects.filter(entity=entity, role=UserRights.ADMIN)
    except Exception:
        raise Exception("Cette société n'a pas d'admin actif")

    send_email_to_admin_users(entity, depot, admins, request)

    return f"Le dépôt {depot.name} est activé et les administrateurs de {entity.name} ont été notifiés"


def send_email_to_admin_users(entity, depot, admins, request):
    today = datetime.now().strftime("%d/%m/%Y")
    subject = f"[CarbuRe][Votre demande de création du dépôt {depot.name}  a été acceptée]"
    subject = subject if CarbureEnv.is_prod else "TEST " + subject
    recipient_list = [admins.email] if CarbureEnv.is_prod else ["carbure@beta.gouv.fr"]
    text_message = f"""
    Bonjour,

    Votre demande de création de dépôt {depot.name} pour la société {entity.name} a été acceptée à la date du {today}.
    Rendez-vous sur la page Société pour ajouter le dépôt à votre liste ou cliquez sur le lien suivant : {CarbureEnv.get_base_url()}/org/{entity.id}/settings#depot

    Pour plus d'information veuillez consulter notre guide d'utilisation : https://carbure-1.gitbook.io/faq/informations-utilisateurs/producteurs-et-traders-parametrer-mon-compte/ajouter-ou-supprimer-un-depot-1

    Bien cordialement,
    L'équipe CarbuRe
    """  # noqa: E501

    send_mail(
        request=request,
        subject=subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )
