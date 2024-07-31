from core.utils import CarbureEnv
from core.models import UserRights
from django.core.mail import send_mail
from django.conf import settings


def enable_depot(depot):
    if depot.is_enabled:
        return f"Le dépôt {depot.name} est déjà activé"

    depot.is_enabled = True
    depot.save()

    # Get entity admin users
    entity = depot.entity
    try:
        admins = UserRights.objects.filter(entity=entity, role=UserRights.ADMIN)
    except:
        raise Exception("Cette société n'a pas d'admin actif")

    # send email to user
    subject = "Votre dépôt est validé"
    subject = subject if CarbureEnv.is_prod else "TEST " + subject
    recipient_list = [admins.email] if CarbureEnv.is_prod else ["carbure@beta.gouv.fr"]
    text_message = f"""
    Bonjour,

    Votre demande de création de dépôt {depot.name} a été validée par l'administration.
    Vous pouvez désormais accéder à la société {entity.name} dans votre espace CarbuRe pour associer ce dépôt.
 
    Pour plus d'information veuillez consulter notre guide d'utilisation : https://carbure-1.gitbook.io/faq/informations-utilisateurs/producteurs-et-traders-parametrer-mon-compte/ajouter-ou-supprimer-un-depot-1

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

    return f"Le dépôt {depot.name} est activé et les administrateurs de {entity.name} ont été notifiés"
