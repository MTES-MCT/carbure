from django.conf import settings
from django.core.mail import send_mail

from core.models import UserRights, UserRightsRequests
from core.utils import CarbureEnv


def enable_entity(entity):
    # get entity admin
    try:
        right_request = UserRightsRequests.objects.get(entity=entity, role=UserRightsRequests.ADMIN, status="PENDING")
    except:
        raise Exception("Cette société n'a pas de demande d'inscription en attente")

    admin_user = right_request.user
    # valid admin rights request
    right_request.status = "ACCEPTED"
    right_request.save()

    # create user right
    UserRights.objects.create(
        entity=right_request.entity,
        user=right_request.user,
        role=right_request.role,
        expiration_date=right_request.expiration_date,
    )

    entity.is_enabled = True
    entity.save()

    # send email to user
    subject = "Demande d'inscription de société enregistrée"
    subject = subject if CarbureEnv.is_prod else "TEST " + subject
    recipient_list = [admin_user.email] if CarbureEnv.is_prod else ["carbure@beta.gouv.fr"]
    text_message = f"""
    Bonjour,

    Votre demande d'inscription pour la société {entity.name} a été validée par l'administration.
    Vous pouvez désormais accéder à la société dans votre espace en tant qu'administrateur : {CarbureEnv.get_base_url()}/account
 
    Pour plus d'information veuillez consulter notre guide d'utilisation : https://carbure-1.gitbook.io/faq/affichage/traduction

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
